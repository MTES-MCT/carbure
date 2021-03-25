# https://django-authtools.readthedocs.io/en/latest/how-to/invitation-email.html
# allows a manual user creation by an admin, without setting a password

from django.contrib import admin
from django.contrib import messages
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.utils.crypto import get_random_string
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render

from authtools.admin import NamedUserAdmin
from authtools.forms import UserCreationForm
from core.models import Entity, UserRights, UserPreferences, Biocarburant, MatierePremiere, Pays, UserRightsRequests
from core.models import GHGValues, Depot, LotV2, LotTransaction, TransactionError, LotV2Error, TransactionComment
from core.models import LotValidationError
from core.models import ISCCScope, ISCCCertificate, ISCCCertificateRawMaterial, ISCCCertificateScope, EntityISCCTradingCertificate
from core.models import DBSCertificate, DBSScope, DBSCertificateScope, EntityDBSTradingCertificate
from core.models import REDCertScope, REDCertBiomassType, REDCertCertificate, REDCertCertificateScope, REDCertCertificateBiomass, EntityREDCertTradingCertificate
from core.models import ProductionSiteCertificate, EntityDepot
from core.models import SustainabilityDeclaration
from api.v3.sanity_checks import bulk_sanity_checks
from core.common import get_prefetched_data

class EntityAdmin(admin.ModelAdmin):
    list_display = ('entity_type', 'name', 'parent_entity')
    search_fields = ('entity_type', 'name')
    list_filter = ('entity_type',)


class UserRightsAdmin(admin.ModelAdmin):
    list_display = ('user', 'entity')
    search_fields = ('user__name', 'entity__name')


class UserRightsRequestsAdmin(admin.ModelAdmin):
    list_display = ('user', 'entity', 'status')
    search_fields = ('user', 'entity', 'status')


class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user', 'default_entity')
    search_fields = ('user__name', 'default_entity__name')


class BiocarburantAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'description', 'is_alcool', 'is_graisse', 'is_displayed')
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


class LotV2ErrorAdmin(admin.ModelAdmin):
    list_display = ('lot', 'field', 'value', 'error')
    search_fields = ('lot__id', 'field', 'value', 'error')
    list_filter = ('field', )
    raw_id_fields = ('lot', )


class LotValidationErrorAdmin(admin.ModelAdmin):
    list_display = ('lot', 'rule_triggered', 'warning_to_user', 'warning_to_admin', 'block_validation')
    list_filter = ('warning_to_admin', 'warning_to_user', 'block_validation')
    search_fields = ('rule_triggered', 'message')
    raw_id_fields = ('lot', )


class GHGValuesAdmin(admin.ModelAdmin):
    list_display = ('matiere_premiere', 'biocarburant', 'condition', 'eec_default', 'ep_default', 'etd_default')
    search_fields = ('matiere_premiere', 'biocarburant')
    list_filter = ('biocarburant',)


class DepotAdmin(admin.ModelAdmin):
    list_display = ('name', 'depot_id', 'city', 'depot_type')
    search_fields = ('name', 'city', 'depot_id')
    list_filter = ('depot_type',)


class LotV2Admin(admin.ModelAdmin):
    list_display = ('period', 'data_origin_entity', 'biocarburant', 'matiere_premiere', 'volume', 'status', 'carbure_production_site', 'unknown_production_site', 'unknown_production_site_reference')
    search_fields = ('carbure_producer__name', 'biocarburant__name', 'matiere_premiere__name', 'carbure_id', 'period',)
    list_filter = ('period', 'production_site_is_in_carbure', 'carbure_producer', 'status', 'source', 'biocarburant', 'matiere_premiere', 'is_split', 'is_fused', 'is_transformed', 'added_by', 'added_by_user')
    raw_id_fields = ('fused_with', 'parent_lot', )
    readonly_fields = ('added_time',)
    actions = ['delete_orphans']


    def delete_orphans(self, request, queryset):
        annotated = queryset.annotate(nb_tx=Count('tx_lot'))
        zeros = annotated.filter(nb_tx=0)
        deleted, _ = zeros.delete()
        self.message_user(request, '%d lots deleted.' % deleted, messages.SUCCESS)
    delete_orphans.short_description = "Supprimer Lots Orphelins"




class TransactionAdmin(admin.ModelAdmin):
    list_display = ('get_lot_mp', 'get_lot_bc', 'get_lot_volume', 'carbure_vendor', 'carbure_client', 'dae', 'carbure_delivery_site', 'delivery_date', 'delivery_status', 'unknown_client', 'carbure_vendor_certificate', 'get_lot_unknown_vendor_certificate')
    search_fields = ('lot__id', 'dae', 'champ_libre')
    list_filter = ('lot__status', 'delivery_status', 'lot__period', 'client_is_in_carbure', 'carbure_vendor', 'carbure_client',  'is_mac', 'is_batch', 'delivery_site_is_in_carbure')
    raw_id_fields = ('lot',)
    actions = ['rerun_sanity_checks', 'delete_ghosts', 'change_transaction_delivery_site', 'change_transaction_client', 'delete_errors', 'assign_transaction_certificate']


    def get_lot_mp(self, obj):
        return obj.lot.matiere_premiere
    get_lot_mp.admin_order_field  = 'FeedStock'
    get_lot_mp.short_description = 'FeedStock'


    def get_lot_bc(self, obj):
        return obj.lot.biocarburant
    get_lot_bc.admin_order_field  = 'BioFuel'
    get_lot_bc.short_description = 'BioFuel'


    def get_lot_volume(self, obj):
        return obj.lot.volume
    get_lot_volume.admin_order_field  = 'Volume'
    get_lot_volume.short_description = 'Volume'    


    def get_lot_unknown_vendor_certificate(self, obj):
        return obj.lot.unknown_supplier_certificate
    get_lot_unknown_vendor_certificate.admin_order_field  = 'Cert. Fournisseur'
    get_lot_unknown_vendor_certificate.short_description = 'Cert. Fournisseur'    


    def rerun_sanity_checks(self, request, queryset):
        d = get_prefetched_data()
        bulk_sanity_checks(queryset, d, background=False)
    rerun_sanity_checks.short_description = "Moulinette Règles Métiers"


    def delete_ghosts(self, request, queryset):
        nb_deleted, _ = queryset.filter(delivery_date=None).delete()
        self.message_user(request, '%d transactions deleted.' % nb_deleted, messages.SUCCESS)
    delete_ghosts.short_description = "Supprimer Transactions Fantômes"


    def delete_errors(self, request, queryset):
        lots = [tx.lot for tx in queryset]
        nb_deleted, _ = LotValidationError.objects.filter(lot__in=lots).delete()
        self.message_user(request, '%d errors deleted.' % nb_deleted, messages.SUCCESS)
    delete_errors.short_description = "Supprimer Erreurs"


    class AssignSupplierCertificateTransactionForm(forms.Form):
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
        certificates = []
        certificate = forms.ChoiceField(choices=certificates)
        
        def __init__(self, *args, **kwargs):
            super(TransactionAdmin.AssignSupplierCertificateTransactionForm, self).__init__(*args, **kwargs)
            certificates = [(c.certificate.certificate_id, '%s - %s' % (c.entity.name, c.certificate.certificate_id)) for c in EntityISCCTradingCertificate.objects.all()]
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
                    TransactionError.objects.filter(tx=tx, field='unknown_supplier_certificate').delete()
                    count += 1
                self.message_user(request, "Successfully assigned certificate to %d." % (count))
                return HttpResponseRedirect(request.get_full_path())
        if not form:
            form = self.AssignSupplierCertificateTransactionForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
        return render(request, 'admin/assign_supplier_certificate_to_transaction.html', {'transactions': queryset, 'change_certificate_form': form})
    assign_transaction_certificate.short_description = "Ajouter Certificat du Fournisseur"


    class ChangeTransactionClientForm(forms.Form):
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
        new_client = forms.ModelChoiceField(Entity.objects.filter(entity_type__in=[Entity.PRODUCER, Entity.OPERATOR, Entity.TRADER]))

    def change_transaction_client(self, request, queryset):
        form = None
        if 'apply' in request.POST:
            form = self.ChangeTransactionClientForm(request.POST)
            if form.is_valid():
                new_client = form.cleaned_data['new_client']
                count = 0
                for tx in queryset:
                    tx.carbure_client = new_client
                    tx.unknown_client = ''
                    tx.delivery_status = 'N'
                    tx.client_is_in_carbure = True
                    tx.save()
                    TransactionError.objects.filter(tx=tx, field='unknown_client').delete()
                    count += 1
                self.message_user(request, "Successfully reassigned %d transactions to %s." % (count, new_client))
                return HttpResponseRedirect(request.get_full_path())
        if not form:
            form = self.ChangeTransactionClientForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
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
            form = self.ChangeTransactionDeliverySiteForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
        return render(request, 'admin/change_transaction_delivery_site.html', {'transactions': queryset, 'change_delivery_site_form': form})
    change_transaction_delivery_site.short_description = "Changer le site de livraison"

class TransactionErrorAdmin(admin.ModelAdmin):
    list_display = ('tx', 'field', 'error', 'value')
    search_fields = ('field', 'error', 'value')
    list_filter = ('field',)
    raw_id_fields = ('tx', )


class TransactionCommentAdmin(admin.ModelAdmin):
    list_display = ('entity', 'tx', 'comment', 'topic')
    search_fields = ('entity', 'tx', 'comment')
    list_filter = ('topic', )
    raw_id_fields = ('tx', )


class ISCCScopeAdmin(admin.ModelAdmin):
    list_display = ('scope', 'description')
    search_fields = ('scope', 'description')


class ISCCCertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'certificate_holder', 'valid_from', 'valid_until')
    search_fields = ('certificate_id', 'certificate_holder', 'issuing_cb')


class ISCCCertificateRawMaterialAdmin(admin.ModelAdmin):
    list_display = ('certificate', 'raw_material')
    search_fields = ('certificate__certificate_id', 'raw_material')
    raw_id_fields = ('certificate', )


class ISCCCertificateScopeAdmin(admin.ModelAdmin):
    list_display = ('certificate', 'scope')
    search_fields = ('certificate__certificate_id', 'certificate__certificate_holder', 'scope__scope')
    raw_id_fields = ('certificate', )


class DBSScopeAdmin(admin.ModelAdmin):
    list_display = ('certification_type', )
    search_fields = ('certification_type', )


class DBSCertificateScopeAdmin(admin.ModelAdmin):
    list_display = ('certificate', 'scope')
    search_fields = ('certificate', 'scope')
    raw_id_fields = ('certificate', )


class DBSCertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'certificate_holder', 'holder_address', 'valid_from', 'valid_until')
    search_fields = ('certificate_id', 'certificate_holder', 'holder_address')


class REDCertScopeAdmin(admin.ModelAdmin):
    list_display = ('scope', 'description_fr', 'description_de', 'description_en')
    search_fields = ('scope', 'description_fr', 'description_de', 'description_en')


class REDCertBiomassTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'description_fr', 'description_de', 'description_en')
    search_fields = ('code', 'description_fr', 'description_de', 'description_en')


class REDCertCertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'certificate_holder', 'city', 'country', 'valid_from', 'valid_until', 'certificator', 'certificate_type', 'status')
    search_fields = ('certificate_id', 'certificate_holder', 'city', 'certificator', 'certificate_type')
    list_filter = ('country', 'status', 'certificate_type')


class REDCertCertificateScopeAdmin(admin.ModelAdmin):
    list_display = ('certificate', 'scope')
    search_fields = ('certificate__certificate_id',)
    list_filter = ('scope', )


class REDCertCertificateBiomassAdmin(admin.ModelAdmin):
    list_display = ('certificate', 'biomass')
    search_fields = ('certificate', 'biomass')
    list_filter = ('biomass', )


class EntityISCCTradingCertificateAdmin(admin.ModelAdmin):
    list_display = ('entity', 'certificate',)
    search_fields = ('entity', 'certificate',)


class EntityDBSTradingCertificateAdmin(admin.ModelAdmin):
    list_display = ('entity', 'certificate',)
    search_fields = ('entity', 'certificate',)


class EntityREDCertTradingCertificateAdmin(admin.ModelAdmin):
    list_display = ('entity', 'certificate',)
    search_fields = ('entity', 'certificate',)


class ProductionSiteCertificateAdmin(admin.ModelAdmin):
    list_display = ('production_site', 'type', 'certificate_iscc', 'certificate_2bs', 'certificate_redcert')
    search_fields = ('production_site', 'certificate_iscc', 'certificate_2bs', 'certificate_redcert')
    list_filter = ('type',)


class SustainabilityDeclarationAdmin(admin.ModelAdmin):
    list_display = ('entity', 'period', 'declared', 'checked', 'deadline')
    search_fields = ('entity', )
    list_filter = ('entity', 'period', 'declared', 'checked')


class EntityDepotAdmin(admin.ModelAdmin):
    list_display = ('entity', 'depot', 'blending_is_outsourced',)
    search_fields = ('entity', 'depot', )
    list_filter = ('blending_is_outsourced', )


admin.site.register(Entity, EntityAdmin)
admin.site.register(UserRights, UserRightsAdmin)
admin.site.register(UserRightsRequests, UserRightsRequestsAdmin)
admin.site.register(UserPreferences, UserPreferencesAdmin)
admin.site.register(Biocarburant, BiocarburantAdmin)
admin.site.register(MatierePremiere, MatierePremiereAdmin)
admin.site.register(Pays, PaysAdmin)
admin.site.register(GHGValues, GHGValuesAdmin)
admin.site.register(Depot, DepotAdmin)
admin.site.register(LotV2, LotV2Admin)
admin.site.register(LotTransaction, TransactionAdmin)
admin.site.register(TransactionError, TransactionErrorAdmin)
admin.site.register(TransactionComment, TransactionCommentAdmin)
admin.site.register(LotV2Error, LotV2ErrorAdmin)
admin.site.register(LotValidationError, LotValidationErrorAdmin)
admin.site.register(ISCCScope, ISCCScopeAdmin)
admin.site.register(ISCCCertificate, ISCCCertificateAdmin)
admin.site.register(ISCCCertificateRawMaterial, ISCCCertificateRawMaterialAdmin)
admin.site.register(ISCCCertificateScope, ISCCCertificateScopeAdmin)
admin.site.register(DBSCertificate, DBSCertificateAdmin)
admin.site.register(DBSScope, DBSScopeAdmin)
admin.site.register(DBSCertificateScope, DBSCertificateScopeAdmin)
admin.site.register(REDCertCertificate, REDCertCertificateAdmin)
admin.site.register(REDCertScope, REDCertScopeAdmin)
admin.site.register(REDCertBiomassType, REDCertBiomassTypeAdmin)
admin.site.register(REDCertCertificateScope, REDCertCertificateScopeAdmin)
admin.site.register(REDCertCertificateBiomass, REDCertCertificateBiomassAdmin)
admin.site.register(EntityISCCTradingCertificate, EntityISCCTradingCertificateAdmin)
admin.site.register(EntityDBSTradingCertificate, EntityDBSTradingCertificateAdmin)
admin.site.register(EntityREDCertTradingCertificate, EntityREDCertTradingCertificateAdmin)
admin.site.register(ProductionSiteCertificate, ProductionSiteCertificateAdmin)
admin.site.register(SustainabilityDeclaration, SustainabilityDeclarationAdmin)
admin.site.register(EntityDepot, EntityDepotAdmin)


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
