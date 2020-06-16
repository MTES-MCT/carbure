# https://django-authtools.readthedocs.io/en/latest/how-to/invitation-email.html
# allows a manual user creation by an admin, without setting a password

from django.contrib import admin
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.utils.crypto import get_random_string
from authtools.admin import NamedUserAdmin
from authtools.forms import UserCreationForm
from core.models import Entity, UserRights, UserPreferences, Biocarburant, MatierePremiere, Pays, Lot, LotComment
from core.models import LotError, GHGValues, Depot, LotV2, LotTransaction, TransactionError, LotV2Error


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
    list_display = ('code', 'name', 'description')
    search_fields = ('name', )
    readonly_fields = ('code', )


class MatierePremiereAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', )
    readonly_fields = ('code', )


class PaysAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )


class LotAdmin(admin.ModelAdmin):
    list_display = ('period', 'carbure_id', 'producer', 'production_site', 'ea_delivery_site', 'ea_delivery_date', 'ea', 'biocarburant', 'matiere_premiere', 'client_id', 'status', 'ea_delivery_status')
    search_fields = ('dae', 'client_id', 'ea_delivery_status', 'carbure_id')
    list_filter = ('producer', 'ea', 'status', 'ea_delivery_status', 'period')


class LotCommentAdmin(admin.ModelAdmin):
    list_display = ('entity', 'lot', 'comment')
    search_fields = ('entity', 'lot', 'comment')


class LotErrorAdmin(admin.ModelAdmin):
    list_display = ('lot', 'field', 'value', 'error')
    search_fields = ('lot', 'field', 'value', 'error')
    list_filter = ('field', )


class LotV2ErrorAdmin(admin.ModelAdmin):
    list_display = ('lot', 'field', 'value', 'error')
    search_fields = ('lot', 'field', 'value', 'error')
    list_filter = ('field', )


class GHGValuesAdmin(admin.ModelAdmin):
    list_display = ('matiere_premiere', 'biocarburant', 'condition', 'eec_default', 'ep_default', 'etd_default')
    search_fields = ('matiere_premiere', 'biocarburant')
    list_filter = ('biocarburant',)


class DepotAdmin(admin.ModelAdmin):
    list_display = ('name', 'depot_id', 'city')
    search_fields = ('name', 'city', 'depot_id')


class LotV2Admin(admin.ModelAdmin):
    list_display = ('period', 'carbure_id', 'carbure_producer', 'carbure_production_site', 'biocarburant', 'matiere_premiere', 'status')
    search_fields = ('carbure_producer', 'biocarburant', 'matiere_premiere', 'carbure_id', 'period')
    list_filter = ('period', 'carbure_producer', 'is_split', 'status', 'source', 'biocarburant', 'is_split', 'is_fused')


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('carbure_vendor', 'carbure_client', 'dae', 'carbure_delivery_site', 'delivery_date', 'delivery_status')
    search_fields = ('lot__id', 'dae', 'champ_libre')
    list_filter = ('carbure_vendor', 'carbure_client', 'delivery_status')


class TransactionErrorAdmin(admin.ModelAdmin):
    list_display = ('tx', 'field', 'error', 'value')
    search_fields = ('field', 'error', 'value')
    list_filter = ('field',)


admin.site.register(Entity, EntityAdmin)
admin.site.register(UserRights, UserRightsAdmin)
admin.site.register(UserPreferences, UserPreferencesAdmin)
admin.site.register(Biocarburant, BiocarburantAdmin)
admin.site.register(MatierePremiere, MatierePremiereAdmin)
admin.site.register(Pays, PaysAdmin)
admin.site.register(Lot, LotAdmin)
admin.site.register(LotComment, LotCommentAdmin)
admin.site.register(LotError, LotErrorAdmin)
admin.site.register(GHGValues, GHGValuesAdmin)
admin.site.register(Depot, DepotAdmin)

admin.site.register(LotV2, LotV2Admin)
admin.site.register(LotTransaction, TransactionAdmin)
admin.site.register(TransactionError, TransactionErrorAdmin)
admin.site.register(LotV2Error, LotV2ErrorAdmin)


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
