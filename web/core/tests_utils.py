from django.contrib.auth import get_user_model
from django.urls import reverse
from django_otp.plugins.otp_email.models import EmailDevice

from core.models import UserRights, UserRightsRequests


def setup_current_user(test, email, name, password, entity_rights=[], is_staff=False):
    User = get_user_model()
    user = User.objects.create_user(email=email, name=name, password=password, is_staff=is_staff)
    loggedin = test.client.login(username=user.email, password=password)
    test.assertTrue(loggedin)

    for entity, role in entity_rights:
        UserRights.objects.update_or_create(entity=entity, user=user, role=role)
        UserRightsRequests.objects.update_or_create(entity=entity, user=user, role=role)

    response = test.client.post(reverse("auth-request-otp"))
    test.assertEqual(response.status_code, 200)
    device, _ = EmailDevice.objects.get_or_create(user=user)
    response = test.client.post(reverse("auth-verify-otp"), {"otp_token": device.token})
    test.assertEqual(response.status_code, 200)

    return user
