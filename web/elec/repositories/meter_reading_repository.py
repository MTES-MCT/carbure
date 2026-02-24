from django.db.models import Count, F, OuterRef, Q, QuerySet, Subquery, Sum, Value
from django.db.models.fields import FloatField, IntegerField
from django.db.models.functions import Coalesce

from core.models import Entity
from elec.models import ElecMeterReadingApplication
from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_meter_reading import ElecMeterReading
from transactions.models.year_config import YearConfig


class MeterReadingRepository:
    @staticmethod
    def get_annotated_applications():
        readings_by_application = (
            ElecMeterReading.extended_objects.filter(application_id=OuterRef("pk"))
            .order_by()
            .values("application_id")
            .annotate(
                energy_total=Sum("renewable_energy"),
                charge_point_count=Count("pk"),
            )
        )

        return ElecMeterReadingApplication.objects.annotate(
            energy_total=Coalesce(
                Subquery(readings_by_application.values("energy_total")[:1]),
                Value(0.0),
                output_field=FloatField(),
            ),
            charge_point_count=Coalesce(
                Subquery(readings_by_application.values("charge_point_count")[:1]),
                Value(0),
                output_field=IntegerField(),
            ),
        ).all()

    @staticmethod
    def get_annotated_applications_details():
        return MeterReadingRepository.get_annotated_applications().annotate(
            power_total=Sum("elec_meter_readings__meter__charge_point__nominal_power"),
        )

    @staticmethod
    def get_annotated_applications_by_cpo(cpo):
        return MeterReadingRepository.get_annotated_applications().filter(cpo=cpo)

    @staticmethod
    def get_cpo_application_for_quarter(cpo, year: int, quarter: int):
        return MeterReadingRepository.get_annotated_applications().filter(cpo=cpo, quarter=quarter, year=year).first()

    @staticmethod
    def get_previous_application(cpo: Entity, quarter=None, year=None):
        applications = ElecMeterReadingApplication.objects.filter(cpo=cpo, status=ElecMeterReadingApplication.ACCEPTED)
        if quarter and year:
            applications = applications.filter(Q(year__lt=year) | (Q(year=year) & Q(quarter__lt=quarter)))
        return applications.order_by("-year", "-quarter").first()

    @staticmethod
    def get_application_meter_readings(cpo: Entity, application: ElecMeterReadingApplication):
        return ElecMeterReading.extended_objects.filter(cpo=cpo, application=application)

    @staticmethod
    def get_application_charge_points(cpo: Entity, application: ElecMeterReadingApplication):
        charge_point_ids = ElecMeterReading.objects.filter(cpo=cpo, application=application).values_list(
            "meter__charge_point_id", flat=True
        )
        return ElecChargePoint.objects.filter(pk__in=charge_point_ids, is_deleted=False)

    @staticmethod
    def get_renewable_share(year: int):
        instance = YearConfig.objects.get(year=year)
        return instance.renewable_share / 100

    @staticmethod
    def get_entities_without_application(quarter, year):
        return Entity.objects.annotate(
            meter_readings_charge_points_count=Count(
                "elec_charge_points",
                filter=Q(elec_charge_points__is_article_2=False, elec_charge_points__is_deleted=False),
                distinct=True,
            ),
            app_count=Count(
                "elec_meter_reading_applications",
                filter=Q(elec_meter_reading_applications__quarter=quarter, elec_meter_reading_applications__year=year),
                distinct=True,
            ),
        ).filter(app_count=0, meter_readings_charge_points_count__gt=0, entity_type=Entity.CPO)

    @staticmethod
    def annotate_charge_points_with_latest_index(charge_points: QuerySet[ElecChargePoint]):
        """Annotate charge points with their latest meter reading index and date from ElecMeterReadingVirtual.

        Falls back to current_meter.initial_index/initial_index_date if no reading exists.
        """
        latest_reading_subquery = ElecMeterReading.extended_objects.filter(charge_point_id=OuterRef("pk")).order_by(
            "-current_index_date"
        )
        return charge_points.select_related("current_meter").annotate(
            latest_reading_index=Coalesce(
                Subquery(latest_reading_subquery.values("current_index")[:1]),
                F("current_meter__initial_index"),
                output_field=FloatField(),
            ),
            latest_reading_date=Coalesce(
                Subquery(latest_reading_subquery.values("current_index_date")[:1]),
                F("current_meter__initial_index_date"),
            ),
        )
