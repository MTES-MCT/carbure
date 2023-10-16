import factory
from datetime import datetime, date

from doublecount.models import DoubleCountingApplication, DoubleCountingDocFile


class DoubleCountingDocFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DoubleCountingDocFile

    url = factory.Faker("url")
    agreement_id = factory.Faker("lexify", text="????????????")
    file_name = "dc_file.xlsx"
    file_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    dca = factory.Iterator(DoubleCountingApplication.objects.all())
    link_expiry_dt =  date(datetime.today().year, 12, 31)
    created_at = datetime.now()


