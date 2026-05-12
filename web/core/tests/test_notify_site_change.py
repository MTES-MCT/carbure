from unittest import TestCase
from unittest.mock import MagicMock, patch

from django import forms

from core.services.notify_site_change import notify_site_change


class SiteChangeForm(forms.Form):
    name = forms.CharField(label="Name")


class NotifySiteChangeTest(TestCase):
    @patch("core.services.notify_site_change.send_mail")
    @patch("core.services.notify_site_change.Entity.objects.filter")
    @patch("core.services.notify_site_change.SafTicket.objects.filter")
    @patch("core.services.notify_site_change.CarbureLot.objects.filter")
    def test_notify_site_change_sends_deduplicated_recipients(
        self,
        lots_filter,
        tickets_filter,
        entity_filter,
        send_mail,
    ):
        form = SiteChangeForm(data={"name": "Updated site"}, initial={"name": "Initial site"})
        self.assertTrue(form.is_valid())

        site_entities = MagicMock()
        site_entities.distinct.return_value = [2]

        site = MagicMock(
            name="Demo site",
            created_by_id=1,
            entitysite_set=MagicMock(values_list=MagicMock(return_value=site_entities)),
        )

        lots = MagicMock()
        lots.values_list.side_effect = [
            MagicMock(distinct=MagicMock(return_value=[3, None])),
            MagicMock(distinct=MagicMock(return_value=[])),
        ]
        lots_filter.return_value = lots

        tickets = MagicMock()
        tickets.values_list.side_effect = [
            MagicMock(distinct=MagicMock(return_value=[4])),
            MagicMock(distinct=MagicMock(return_value=[])),
        ]
        tickets_filter.return_value = tickets

        entity_1 = MagicMock()
        entity_1.get_users_emails.return_value = ["admin@example.com", "shared@example.com"]
        entity_2 = MagicMock()
        entity_2.get_users_emails.return_value = ["rw@example.com", "shared@example.com"]
        entity_filter.return_value = [entity_1, entity_2]

        notify_site_change(site, form)

        entity_filter.assert_called_once_with(id__in={1, 2, 3, 4})
        send_mail.assert_called_once()
        recipient_list = send_mail.call_args.kwargs["recipient_list"]
        self.assertCountEqual(
            recipient_list,
            ["admin@example.com", "rw@example.com", "shared@example.com"],
        )
