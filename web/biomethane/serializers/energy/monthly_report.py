from django.utils.translation import gettext as _
from rest_framework import serializers

from biomethane.models import BiomethaneEnergyMonthlyReport


class BiomethaneEnergyMonthlyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomethaneEnergyMonthlyReport
        exclude = ["id"]


class MonthlyReportDataSerializer(serializers.Serializer):
    month = serializers.IntegerField(min_value=1, max_value=12)
    injected_volume_nm3 = serializers.FloatField()
    average_monthly_flow_nm3_per_hour = serializers.FloatField()
    injection_hours = serializers.FloatField()


class BiomethaneEnergyMonthlyReportInputSerializer(serializers.ListSerializer):
    child = MonthlyReportDataSerializer()

    def validate(self, attrs):
        months = [item["month"] for item in attrs]
        if len(months) != len(set(months)):
            raise serializers.ValidationError(_("Chaque mois ne peut apparaître qu'une seule fois"))

        energy_instance = self.context.get("energy")
        if not energy_instance:
            raise serializers.ValidationError(
                {"energy": [_("Cette entité n'a pas de déclaration énergétique pour cette année.")]}
            )
        return attrs

    def create(self, validated_data):
        energy_instance = self.context.get("energy")
        created_reports = []

        # Upsert all monthly reports
        for month_data in validated_data:
            report_data = {
                "injected_volume_nm3": month_data["injected_volume_nm3"],
                "average_monthly_flow_nm3_per_hour": month_data["average_monthly_flow_nm3_per_hour"],
                "injection_hours": month_data["injection_hours"],
            }

            report, created = BiomethaneEnergyMonthlyReport.objects.update_or_create(
                energy=energy_instance, month=month_data["month"], defaults=report_data
            )
            created_reports.append(report)

        return created_reports
