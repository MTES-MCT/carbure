# https://django-authtools.readthedocs.io/en/latest/how-to/invitation-email.html
# allows a manual user creation by an admin, without setting a password

import datetime
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.filters import DateFieldListFilter
from django.db.models import Q
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.utils.crypto import get_random_string
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedOnlyDropdownFilter, ChoiceDropdownFilter
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME


from authtools.admin import NamedUserAdmin
from authtools.forms import UserCreationForm
from core.models import Entity, ExternalAdminRights, UserRights, UserPreferences, Biocarburant, MatierePremiere, Pays, UserRightsRequests
from core.models import Depot, LotV2, LotTransaction, TransactionComment, GenericError
from core.models import SustainabilityDeclaration, EntityDepot
from core.models import TransactionUpdateHistory, TransactionDistance
from core.models import EmailNotification, ETBETransformation
from certificates.models import EntitySNTradingCertificate, EntityISCCTradingCertificate, EntityDBSTradingCertificate, EntityREDCertTradingCertificate
from api.v3.sanity_checks import bulk_sanity_checks
from core.common import get_prefetched_data, calculate_ghg

class EntityAdmin(admin.ModelAdmin):
    list_display = ('entity_type', 'name', 'parent_entity')
    search_fields = ('entity_type', 'name')
    list_filter = ('entity_type',)


class UserRightsAdmin(admin.ModelAdmin):
    list_display = ('user', 'entity')
    search_fields = ('user__name', 'entity__name')


class UserRightsRequestsAdmin(admin.ModelAdmin):
    list_display = ('user', 'entity', 'status')
    search_fields = ('user__name', 'entity__name', 'status')


class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user', 'default_entity')
    search_fields = ('user__name', 'default_entity__name')


class BiocarburantAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'description', 'is_alcool', 'is_graisse', 'is_displayed', 'compatible_essence', 'compatible_diesel')
    search_fields = ('name', )
    readonly_fields = ('code', )
    list_filter = ('is_alcool', 'is_graisse', 'is_displayed')


class MatierePremiereAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'description', 'compatible_alcool', 'compatible_graisse', 'is_double_compte', 'is_huile_vegetale', 'is_displayed')
    search_fields = ('name', )
    readonly_fields = ('code', )
    list_filter = ('compatible_alcool', 'compatible_graisse', 'is_double_compte', 'is_huile_vegetale', 'is_displayed')


class PaysAdmin(admin.ModelAdmin):
    list_display = ('name', 'code_pays', 'is_in_europe')
    search_fields = ('name', 'code_pays', )
    list_filter = ('is_in_europe', )


class DepotAdmin(admin.ModelAdmin):
    list_display = ('name', 'depot_id', 'city', 'depot_type', 'gps_coordinates')
    search_fields = ('name', 'city', 'depot_id')
    list_filter = ('depot_type',)


class LotV2Admin(admin.ModelAdmin):
    list_display = ('period', 'data_origin_entity', 'biocarburant', 'matiere_premiere', 'volume', 'status', 'carbure_production_site', 'unknown_production_site', 'unknown_production_site_reference')
    search_fields = ('carbure_producer__name', 'biocarburant__name', 'matiere_premiere__name', 'carbure_id', 'period',)
    list_filter = ('period', 'production_site_is_in_carbure', 'carbure_producer', 'status', 'source', 'biocarburant', 'matiere_premiere', 'is_split', 'is_fused', 'is_transformed', 'added_by', 'added_by_user')
    raw_id_fields = ('fused_with', 'parent_lot', )
    readonly_fields = ('added_time',)
    actions = ['delete_orphans', 'recalc_ges']


    def delete_orphans(self, request, queryset):
        annotated = queryset.annotate(nb_tx=Count('tx_lot'))
        zeros = annotated.filter(nb_tx=0)
        deleted, _ = zeros.delete()
        self.message_user(request, '%d lots deleted.' % deleted, messages.SUCCESS)
    delete_orphans.short_description = "Supprimer Lots Orphelins"

    def recalc_ges(self, request, queryset):
        for lot in queryset:
            calculate_ghg(lot)
            lot.save()
        self.message_user(request, '%d lots updated.' % queryset.count(), messages.SUCCESS)
    recalc_ges.short_description = "Recalculer GES"


class NameSortedRelatedOnlyDropdownFilter(RelatedOnlyDropdownFilter):
    template = 'django_admin_listfilter_dropdown/dropdown_filter.html'

    def choices(self, changelist):
        data = list(super(RelatedOnlyDropdownFilter, self).choices(changelist))
        # all elements except select-all
        tosort = [x for x in data if x['display'] != _('All')]
        sortedlist = sorted(tosort, key=lambda x: x['display'])
        selectall = data[0]
        sortedlist.insert(0, selectall)
        return sortedlist

class TxPartOfForwardListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Forwarded')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'part_of_forward'

    def lookups(self, request, model_admin):
        return (
            ('Yes', _('yes')),
            ('No', _('no')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(Q(is_forwarded=True) | Q(parent_tx__isnull=False))
        if self.value() == 'No':
            return queryset.filter(Q(is_forwarded=False) | Q(parent_tx__isnull=True))

class UnknownClientListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Unknown Client')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'unknown_client'

    def lookups(self, request, model_admin):
        return (
            ('Yes', _('yes')),
            ('No', _('no')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(carbure_client__isnull=True)
        if self.value() == 'No':
            return queryset.filter(carbure_client__isnull=False)

class UnknownDeliverySiteListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Unknown Delivery Site')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'unknown_delivery_site'

    def lookups(self, request, model_admin):
        return (
            ('Yes', _('yes')),
            ('No', _('no')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(carbure_delivery_site__isnull=True)
        if self.value() == 'No':
            return queryset.filter(carbure_delivery_site__isnull=False)


class UnknownProductionSiteListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Unknown Production Site')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'unknown_production_site'

    def lookups(self, request, model_admin):
        return (
            ('Yes', _('yes')),
            ('No', _('no')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(lot__carbure_production_site__isnull=True)
        if self.value() == 'No':
            return queryset.filter(lot__carbure_production_site__isnull=False)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('get_lot_period', 'get_lot_mp', 'get_lot_bc', 'get_lot_volume', 'get_lot_supplier', 'carbure_vendor', 'get_production_site', 'carbure_client', 'dae', 'carbure_delivery_site', 'unknown_delivery_site', 'delivery_date', 'delivery_status', 'unknown_client', 'carbure_vendor_certificate', 'get_lot_unknown_vendor_certificate')
    search_fields = ('lot__id', 'dae', 'champ_libre', 'lot__carbure_id', 'lot__volume')
    list_filter = ('lot__year', 'lot__status', ('lot__biocarburant', NameSortedRelatedOnlyDropdownFilter), ('lot__matiere_premiere', NameSortedRelatedOnlyDropdownFilter), 'delivery_status', ('lot__period', DropdownFilter), 'client_is_in_carbure', 
                  ('carbure_vendor', NameSortedRelatedOnlyDropdownFilter), ('carbure_client', NameSortedRelatedOnlyDropdownFilter),  'is_mac', 'is_batch', 'delivery_site_is_in_carbure', ('carbure_delivery_site', NameSortedRelatedOnlyDropdownFilter), 
                  ('lot__carbure_production_site', NameSortedRelatedOnlyDropdownFilter), TxPartOfForwardListFilter, UnknownDeliverySiteListFilter, UnknownClientListFilter, UnknownProductionSiteListFilter)
    raw_id_fields = ('lot', 'parent_tx', 'child_tx')
    actions = ['rerun_sanity_checks', 'delete_ghosts', 'change_transaction_delivery_site', 'change_transaction_client', 'assign_transaction_certificate', 'change_transaction_delivery_status']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(TransactionAdmin, self).get_search_results(request, queryset, search_term)
        try:
            date = datetime.datetime.strptime(search_term, '%d/%m/%Y').date()
            queryset |= self.model.objects.filter(Q(lot__unknown_production_site_com_date=date) | Q(lot__carbure_production_site__date_mise_en_service=date))
        except:
            pass
        return queryset, use_distinct


    def get_lot_period(self, obj):
        return obj.lot.period
    get_lot_period.admin_order_field  = 'lot__period'
    get_lot_period.short_description = 'Period'


    def get_lot_mp(self, obj):
        return obj.lot.matiere_premiere
    get_lot_mp.admin_order_field  = 'lot__matiere_premiere__name'
    get_lot_mp.short_description = 'FeedStock'


    def get_lot_bc(self, obj):
        return obj.lot.biocarburant
    get_lot_bc.admin_order_field  = 'lot__biocarburant__name'
    get_lot_bc.short_description = 'BioFuel'


    def get_lot_volume(self, obj):
        return obj.lot.volume
    get_lot_volume.admin_order_field  = 'lot__volume'
    get_lot_volume.short_description = 'Volume'    


    def get_lot_supplier(self, obj):
        return '%s - %s' % (obj.lot.unknown_supplier, obj.lot.unknown_supplier_certificate)
    get_lot_supplier.admin_order_field  = 'lot__unknown_supplier_certificate'
    get_lot_supplier.short_description = 'Unknown Supplier'


    def get_production_site(self, obj):
        psite = ''
        if obj.lot.production_site_is_in_carbure:
            psite = obj.lot.carbure_production_site.name
        elif obj.lot.unknown_production_site:
            psite = obj.lot.unknown_production_site
        else:
            psite = obj.lot.unknown_production_site_reference
        return psite
    get_production_site.admin_order_field  = 'lot__carbure_production_site__name'
    get_production_site.short_description = 'Production Site'


    def get_lot_unknown_vendor_certificate(self, obj):
        return obj.lot.unknown_supplier_certificate
    get_lot_unknown_vendor_certificate.admin_order_field  = 'lot__unknown_supplier_certificate'
    get_lot_unknown_vendor_certificate.short_description = 'Cert. Fournisseur'    


    def rerun_sanity_checks(self, request, queryset):
        d = get_prefetched_data()
        bulk_sanity_checks(queryset, d, background=False)
    rerun_sanity_checks.short_description = "Moulinette Règles Métiers"


    def delete_ghosts(self, request, queryset):
        nb_deleted, _ = queryset.filter(delivery_date=None).delete()
        self.message_user(request, '%d transactions deleted.' % nb_deleted, messages.SUCCESS)
    delete_ghosts.short_description = "Supprimer Transactions Fantômes"


    class AssignSupplierCertificateTransactionForm(forms.Form):
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
        certificates = []
        certificate = forms.ChoiceField(choices=certificates)
        
        def __init__(self, *args, **kwargs):
            super(TransactionAdmin.AssignSupplierCertificateTransactionForm, self).__init__(*args, **kwargs)
            certificates = [(c.certificate.certificate_id, '%s - %s' % (c.entity.name, c.certificate.certificate_id)) for c in EntityISCCTradingCertificate.objects.all()]
            certificates += [(c.certificate.certificate_id, '%s - %s' % (c.entity.name, c.certificate.certificate_id)) for c in EntityDBSTradingCertificate.objects.all()]
            certificates += [(c.certificate.certificate_id, '%s - %s' % (c.entity.name, c.certificate.certificate_id)) for c in EntityREDCertTradingCertificate.objects.all()]
            certificates += [(c.certificate.certificate_id, '%s - %s' % (c.entity.name, c.certificate.certificate_id)) for c in EntitySNTradingCertificate.objects.all()]
            self.fields['certificate'].choices = certificates
            
            
    def assign_transaction_certificate(self, request, queryset):
        form = None
        if 'apply' in request.POST:
            form = self.AssignSupplierCertificateTransactionForm(request.POST)
            if form.is_valid():
                certificate = form.cleaned_data['certificate']
                count = 0
                for tx in queryset:
                    tx.carbure_vendor_certificate = certificate
                    tx.save()
                    GenericError.objects.filter(tx=tx, field='unknown_supplier_certificate').delete()
                    count += 1
                self.message_user(request, "Successfully assigned certificate to %d." % (count))
                return HttpResponseRedirect(request.get_full_path())
        if not form:
            form = self.AssignSupplierCertificateTransactionForm(initial={'_selected_action': request.POST.getlist(ACTION_CHECKBOX_NAME)})
        return render(request, 'admin/assign_supplier_certificate_to_transaction.html', {'transactions': queryset, 'change_certificate_form': form})
    assign_transaction_certificate.short_description = "Ajouter Certificat du Fournisseur"


    class ChangeTransactionClientForm(forms.Form):
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
        new_client = forms.ModelChoiceField(Entity.objects.filter(entity_type__in=[Entity.PRODUCER, Entity.OPERATOR, Entity.TRADER]), required=False)
        unknown_client = forms.CharField(required=False)
        is_unknown_client = forms.BooleanField(initial=False, required=False)

    def change_transaction_client(self, request, queryset):
        form = None
        if 'apply' in request.POST:
            form = self.ChangeTransactionClientForm(request.POST)
            if form.is_valid():
                new_client = form.cleaned_data['new_client']
                unknown_client = form.cleaned_data['unknown_client']
                is_unknown_client = form.cleaned_data['is_unknown_client']
                count = 0
                for tx in queryset:
                    if is_unknown_client:
                        tx.unknown_client = unknown_client
                        tx.carbure_client = None
                        tx.client_is_in_carbure = False
                        tx.delivery_status = LotTransaction.ACCEPTED
                    else:
                        tx.carbure_client = new_client
                        tx.unknown_client = ''
                        tx.client_is_in_carbure = True
                        tx.delivery_status = LotTransaction.PENDING
                        GenericError.objects.filter(tx=tx, field='unknown_client').delete()
                    tx.save()
                    count += 1
                self.message_user(request, "Successfully reassigned %d transactions to %s." % (count, new_client))
                return HttpResponseRedirect(request.get_full_path())
        if not form:
            form = self.ChangeTransactionClientForm(initial={'_selected_action': request.POST.getlist(ACTION_CHECKBOX_NAME)})
        return render(request, 'admin/change_transaction_client.html', {'transactions': queryset, 'change_client_form': form})
    change_transaction_client.short_description = "Changer le client"


    class ChangeTransactionDeliverySiteForm(forms.Form):
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
        new_delivery_site = forms.ModelChoiceField(Depot.objects.all())

    def change_transaction_delivery_site(self, request, queryset):
        form = None
        if 'apply' in request.POST:
            form = self.ChangeTransactionDeliverySiteForm(request.POST)
            if form.is_valid():
                new_delivery_site = form.cleaned_data['new_delivery_site']
                count = 0
                for tx in queryset:
                    tx.delivery_site_is_in_carbure = True
                    tx.carbure_delivery_site = new_delivery_site
                    tx.unknown_delivery_site = ''
                    tx.save()
                    count += 1
                self.message_user(request, "Successfully reassigned %d transactions to %s." % (count, new_delivery_site))
                return HttpResponseRedirect(request.get_full_path())
        if not form:
            form = self.ChangeTransactionDeliverySiteForm(initial={'_selected_action': request.POST.getlist(ACTION_CHECKBOX_NAME)})
        return render(request, 'admin/change_transaction_delivery_site.html', {'transactions': queryset, 'change_delivery_site_form': form})
    change_transaction_delivery_site.short_description = "Changer le site de livraison"


    class ChangeTransactionStatusForm(forms.Form):
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
        new_status = forms.ChoiceField(choices=LotTransaction.DELIVERY_STATUS)

    def change_transaction_delivery_status(self, request, queryset):
        form = None
        if 'apply' in request.POST:
            form = self.ChangeTransactionStatusForm(request.POST)
            if form.is_valid():
                new_status = form.cleaned_data['new_status']
                count = queryset.update(delivery_status=new_status)
                self.message_user(request, "Successfully updated %d transactions to %s." % (count, new_status))
                return HttpResponseRedirect(request.get_full_path())
        if not form:
            form = self.ChangeTransactionStatusForm(initial={'_selected_action': request.POST.getlist(ACTION_CHECKBOX_NAME)})
        return render(request, 'admin/change_transaction_delivery_status.html', {'transactions': queryset, 'change_delivery_status_form': form})
    change_transaction_delivery_status.short_description = "Changer le statut de la livraison"


class TransactionCommentAdmin(admin.ModelAdmin):
    list_display = ('entity', 'tx', 'comment', 'topic')
    search_fields = ('entity__name', 'tx__lot__carbure_id', 'comment')
    list_filter = ('topic', )
    raw_id_fields = ('tx', )


class GenericErrorAdmin(admin.ModelAdmin):
    list_display = ('tx', 'error', 'is_blocking', 'display_to_creator', 'display_to_recipient')
    search_fields = ('tx__lot__carbure_id', 'error', 'extra')
    list_filter = ('error', 'is_blocking', )
    raw_id_fields = ('tx', )


class SustainabilityDeclarationAdmin(admin.ModelAdmin):
    date_hierarchy = 'period'
    list_display = ('entity', 'period', 'declared', 'checked', 'deadline')
    search_fields = ('entity__name', )
    list_filter = (('period', DropdownFilter), 'declared', 'checked', 'entity')
    actions = ['validate_declarations', 'invalidate_declarations']

    def validate_declarations(self, request, queryset):
        for declaration in queryset:
            LotTransaction.objects.filter(lot__period=declaration.period.strftime('%Y-%m')).filter(Q(carbure_client=declaration.entity) | Q(carbure_vendor=declaration.entity)).exclude(delivery_status__in=[LotTransaction.FROZEN]).exclude(lot__status=LotV2.DRAFT).update(delivery_status=LotTransaction.FROZEN)
            declaration.declared = True
            declaration.save()
    validate_declarations.short_description = "Valider les déclarations"

    def invalidate_declarations(self, request, queryset):
        for declaration in queryset:
            LotTransaction.objects.filter(lot__period=declaration.period.strftime('%Y-%m')).filter(Q(carbure_client=declaration.entity) | Q(carbure_vendor=declaration.entity), delivery_status=LotTransaction.FROZEN).update(delivery_status=LotTransaction.ACCEPTED)
            declaration.declared = False
            declaration.checked = False
            declaration.save()
    invalidate_declarations.short_description = "Invalider les déclarations"



class EntityDepotAdmin(admin.ModelAdmin):
    list_display = ('entity', 'depot', 'blending_is_outsourced',)
    search_fields = ('entity__name', 'depot__name', )
    list_filter = ('blending_is_outsourced', )


class TransactionUpdateHistoryAdmin(admin.ModelAdmin):
    list_display = ('tx', 'update_type', 'datetime', 'field', 'value_before', 'value_after')
    search_fields = ('field', 'value_before', 'value_after', )
    list_filter = ('update_type', 'field', )


class TransactionDistanceAdmin(admin.ModelAdmin):
    list_display = ('starting_point', 'delivery_point', 'distance')
    search_fields = ('starting_point', 'delivery_point', )


admin.site.register(Entity, EntityAdmin)
admin.site.register(UserRights, UserRightsAdmin)
admin.site.register(UserRightsRequests, UserRightsRequestsAdmin)
admin.site.register(UserPreferences, UserPreferencesAdmin)
admin.site.register(Biocarburant, BiocarburantAdmin)
admin.site.register(MatierePremiere, MatierePremiereAdmin)
admin.site.register(Pays, PaysAdmin)
admin.site.register(Depot, DepotAdmin)
admin.site.register(LotV2, LotV2Admin)
admin.site.register(LotTransaction, TransactionAdmin)
admin.site.register(TransactionComment, TransactionCommentAdmin)
admin.site.register(GenericError, GenericErrorAdmin)
admin.site.register(SustainabilityDeclaration, SustainabilityDeclarationAdmin)
admin.site.register(EntityDepot, EntityDepotAdmin)
admin.site.register(TransactionUpdateHistory, TransactionUpdateHistoryAdmin)
admin.site.register(TransactionDistance, TransactionDistanceAdmin)


# authtool custom user model
User = get_user_model()


class UserCreationForm(UserCreationForm):
    """
    A UserCreationForm with optional password inputs.
    """

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        # If one field gets autocompleted but not the other, our 'neither
        # password or both password' validation will be triggered.
        self.fields['password1'].widget.attrs['autocomplete'] = 'off'
        self.fields['password2'].widget.attrs['autocomplete'] = 'off'

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = super(UserCreationForm, self).clean_password2()
        if bool(password1) ^ bool(password2):
            raise forms.ValidationError("Fill out both fields")
        return password2


class UserAdmin(NamedUserAdmin):
    """
    A UserAdmin that sends a password-reset email when creating a new user,
    unless a password was entered.
    """
    add_form = UserCreationForm
    add_fieldsets = (
        (None, {
            'description': (
                "Enter the new user's name and email address and click save."
                " The user will be emailed a link allowing them to login to"
                " the site and set their password."
            ),
            'fields': ('email', 'name',),
        }),
        ('Password', {
            'description': "Optionally, you may set the user's password here.",
            'fields': ('password1', 'password2'),
            'classes': ('collapse', 'collapse-closed'),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change and not obj.has_usable_password():
            # Django's PasswordResetForm won't let us reset an unusable
            # password. We set it above super() so we don't have to save twice.
            obj.set_password(get_random_string())
            reset_password = True
        else:
            reset_password = False

        super(UserAdmin, self).save_model(request, obj, form, change)

        if reset_password:
            reset_form = PasswordResetForm({'email': obj.email})
            assert reset_form.is_valid()
            reset_form.save(
                subject_template_name='registration/account_creation_subject.txt',
                email_template_name='registration/account_creation_email.html',
            )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ('entity', 'notif_type')
    list_filter = ('notif_type', )
    raw_id_fields = ['linked_tx']

@admin.register(ETBETransformation)
class ETBETransformation(admin.ModelAdmin):
    list_display = ('added_by', 'previous_stock', 'new_stock', 'volume_ethanol', 'volume_etbe', 'volume_denaturant', 'added_time')
    list_filter = ('added_by', )
    raw_id_fields = ['previous_stock', 'new_stock']
    actions = ['cancel_transformations']

    def cancel_transformations(self, request, queryset):
        for transformation in queryset:
            transformation.previous_stock.lot.remaining_volume = round(transformation.previous_stock.lot.remaining_volume + transformation.volume_ethanol, 2)
            transformation.previous_stock.lot.save()
            transformation.new_stock.lot.delete()
            transformation.new_stock.delete()
            transformation.delete()
    cancel_transformations.short_description = "Annuler Transformation"

@admin.register(ExternalAdminRights)
class ExtAdminRightsAdmin(admin.ModelAdmin):
    list_display = ('entity', 'right',)

