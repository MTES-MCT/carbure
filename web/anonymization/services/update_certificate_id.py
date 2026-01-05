# Update all columns related to a certificate_id to be anonymized
# CarbureLot.production_site_double_counting_certificate
# Site.dc_number
# Site.dc_reference
# DoubleCountingApplication.certificate_id
# DoubleCountingRegistration.certificate_id

from certificates.models import DoubleCountingRegistration
from doublecount.models import DoubleCountingApplication
from transactions.models import Site
from core.models import CarbureLot


def update_certificate_ids():