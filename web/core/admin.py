# https://django-authtools.readthedocs.io/en/latest/how-to/invitation-email.html
# allows a manual user creation by an admin, without setting a password

from django.contrib import admin
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.utils.crypto import get_random_string
from authtools.admin import NamedUserAdmin
from authtools.forms import UserCreationForm
from core.models import Entity, UserRights, UserPreferences, Biocarburant, MatierePremiere, Pays
from core.models import GHGValues, Depot, LotV2, LotTransaction, TransactionError, LotV2Error, TransactionComment
from core.models import LotValidationError
from core.models import ISCCScope, ISCCCertificate, ISCCCertificateRawMaterial, ISCCCertificateScope, DBSCertificate
from core.models import EntityISCCTradingCertificate, EntityDBSTradingCertificate
from api.v3.sanity_checks import queryset_sanity_check


class EntityAdmin(admin.ModelAdmin):
    list_display = ('entity_type', 'name', 'parent_entity')
    search_fields = ('entity_type', 'name')
    list_filter = ('entity_type',)


class UserRightsAdmin(admin.ModelAdmin):
    list_display = ('user', 'entity')
    search_fields = ('user', 'entity')


class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user', 'default_entity')
    search_fields = ('user', 'default_entity')


class BiocarburantAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'description', 'is_alcool', 'is_graisse')
    search_fields = ('name', )
    readonly_fields = ('code', )
    list_filter = ('is_alcool', 'is_graisse', )


class MatierePremiereAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'description', 'compatible_alcool', 'compatible_graisse')
    search_fields = ('name', )
    readonly_fields = ('code', )
    list_filter = ('compatible_alcool', 'compatible_graisse', 'is_double_compte')


class PaysAdmin(admin.ModelAdmin):
    list_display = ('name', 'code_pays', 'is_in_europe')
    search_fields = ('name', 'code_pays', )
    list_filter = ('is_in_europe', )


class LotV2ErrorAdmin(admin.ModelAdmin):
    list_display = ('lot', 'field', 'value', 'error')
    search_fields = ('lot', 'field', 'value', 'error')
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


def reset_checked_status(modeladmin, request, queryset):
    queryset.update(blocking_sanity_checked_passed=False)
    queryset.update(nonblocking_sanity_checked_passed=False)


def admin_run_sanity_checks(modeladmin, request, queryset):
    queryset_sanity_check(queryset)


reset_checked_status.short_description = "Reset sanity checks status"
admin_run_sanity_checks.short_description = "Run sanity checks"


class LotV2Admin(admin.ModelAdmin):
    list_display = ('period', 'carbure_id', 'carbure_producer', 'carbure_production_site', 'biocarburant', 'matiere_premiere', 'status', 'blocking_sanity_checked_passed', 'nonblocking_sanity_checked_passed')
    search_fields = ('carbure_producer__name', 'biocarburant__name', 'matiere_premiere__name', 'carbure_id', 'period', 'added_by_user_email')
    list_filter = ('period', 'carbure_producer', 'is_split', 'status', 'source', 'biocarburant', 'matiere_premiere', 'is_split', 'is_fused', 'blocking_sanity_checked_passed', 'nonblocking_sanity_checked_passed', 'is_valid', 'added_by', 'added_by_user')
    actions = [admin_run_sanity_checks, reset_checked_status]
    raw_id_fields = ('fused_with', 'parent_lot', )


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('carbure_vendor', 'carbure_client', 'dae', 'carbure_delivery_site', 'delivery_date', 'delivery_status')
    search_fields = ('lot__id', 'dae', 'champ_libre')
    list_filter = ('carbure_vendor', 'carbure_client', 'delivery_status', 'is_mac', 'is_batch')
    raw_id_fields = ('lot',)


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
    search_fields = ('certificate', 'raw_material')
    raw_id_fields = ('certificate', )


class ISCCCertificateScopeAdmin(admin.ModelAdmin):
    list_display = ('certificate', 'scope')
    search_fields = ('certificate', 'scope')
    raw_id_fields = ('certificate', )


class DBSCertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'certificate_holder', 'valid_from', 'valid_until')
    search_fields = ('certificate_id', 'certificate_holder',)


class EntityISCCTradingCertificateAdmin(admin.ModelAdmin):
    list_display = ('entity', 'certificate',)
    search_fields = ('entity', 'certificate',)


class EntityDBSTradingCertificateAdmin(admin.ModelAdmin):
    list_display = ('entity', 'certificate',)
    search_fields = ('entity', 'certificate',)


admin.site.register(Entity, EntityAdmin)
admin.site.register(UserRights, UserRightsAdmin)
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
admin.site.register(EntityISCCTradingCertificate, EntityISCCTradingCertificateAdmin)
admin.site.register(EntityDBSTradingCertificate, EntityDBSTradingCertificateAdmin)


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
