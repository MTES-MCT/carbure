from django.utils.translation import gettext_lazy as _

from traceability.serializers.fields import LookupSlugRelatedField


class MaterialLookupField(LookupSlugRelatedField):
    slug_field = "name"
    lookup = "material"
    default_error_messages = {"does_not_exist": _("Matière inconnue")}


class CertificateLookupField(LookupSlugRelatedField):
    slug_field = "certificate_id"
    lookup = "certificate"
    default_error_messages = {"does_not_exist": _("Certificat inconnu")}


class SiteLookupField(LookupSlugRelatedField):
    slug_field = "name"
    lookup = "site"
    default_error_messages = {"does_not_exist": _("Site inconnu")}
