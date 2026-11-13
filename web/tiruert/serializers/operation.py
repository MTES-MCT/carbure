from datetime import datetime

from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from core.models import Biocarburant, MatierePremiere, Pays
from core.models.lot import CarbureLot
from core.serializer_fields import CachedPrimaryKeyRelatedField
from core.serializers import CountrySerializer
from core.utils import check_file_size_and_extension
from tiruert.models import Operation, OperationDetail
from tiruert.serializers.balance import BalanceBiofuelSerializer
from tiruert.serializers.fields import TruncatedFloatField
from tiruert.serializers.operation_detail import OperationDetailSerializer
from tiruert.services.operation import OperationService
from tiruert.services.operation_excel_template import get_tiruert_operator_queryset


class OperationDepotSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class OperationEntitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class OperationDebtLotSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    carbure_id = serializers.CharField()


class OperationDebtSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    lot = OperationDebtLotSerializer()


class BaseOperationSerializer(serializers.ModelSerializer):
    from_depot = OperationDepotSerializer()
    to_depot = OperationDepotSerializer()
    credited_entity = OperationEntitySerializer()
    debited_entity = OperationEntitySerializer()
    details = OperationDetailSerializer(many=True, required=False)
    sector = serializers.CharField(source="_sector", read_only=True)
    type = serializers.CharField(source="_type", read_only=True)
    biofuel = BalanceBiofuelSerializer(read_only=True)
    volume = serializers.SerializerMethodField()
    energy = serializers.SerializerMethodField()
    _entity = serializers.CharField(read_only=True)
    _depot = serializers.CharField(read_only=True)
    avoided_emissions = serializers.SerializerMethodField()
    corrected_avoided_emissions = serializers.FloatField(read_only=True, allow_null=True)
    ghg_delta = serializers.FloatField(read_only=True, allow_null=True)
    year = serializers.IntegerField(source="declaration_year", read_only=True)
    transaction = serializers.CharField(read_only=True, source="_transaction")

    def get_volume(self, instance) -> float:
        return instance.volume

    def get_energy(self, instance) -> float:
        return instance.energy

    def get_avoided_emissions(self, instance) -> float:
        return instance.avoided_emissions


class OperationListSerializer(BaseOperationSerializer):
    volume = TruncatedFloatField(source="_volume", read_only=True)
    energy = TruncatedFloatField(source="_energy", read_only=True, decimal_places=0)
    avoided_emissions = TruncatedFloatField(source="_avoided_emissions", read_only=True)

    def get_fields(self):
        fields = super().get_fields()
        if not self.context.get("details"):
            fields.pop("details", None)
        return fields

    class Meta:
        model = Operation
        fields = [
            "id",
            "type",
            "status",
            "sector",
            "objective_sector",
            "customs_category",
            "biofuel",
            "renewable_energy_share",
            "credited_entity",
            "debited_entity",
            "_entity",
            "from_depot",
            "to_depot",
            "_depot",
            "export_country",
            "created_at",
            "volume",
            "energy",
            "details",
            "avoided_emissions",
            "corrected_avoided_emissions",
            "ghg_delta",
            "year",
            "transaction",
        ]


class OperationSerializer(BaseOperationSerializer):
    corrected_operation_ids = serializers.ListField(child=serializers.IntegerField(), read_only=True, default=list)

    class Meta:
        model = Operation
        fields = [
            "id",
            "type",
            "status",
            "sector",
            "objective_sector",
            "customs_category",
            "biofuel",
            "renewable_energy_share",
            "credited_entity",
            "debited_entity",
            "_entity",
            "from_depot",
            "to_depot",
            "_depot",
            "export_country",
            "export_recipient",
            "created_at",
            "validation_date",
            "durability_period",
            "volume",
            "energy",
            "avoided_emissions",
            "corrected_avoided_emissions",
            "ghg_delta",
            "corrected_operation_ids",
            "details",
            "year",
            "devaluation_type",
            "debt",
            "transaction",
        ]

    export_country = CountrySerializer(read_only=True)
    debt = OperationDebtSerializer(read_only=True, allow_null=True)


class OperationLotSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    volume = serializers.FloatField()


class OperationExcelImportRequestSerializer(serializers.Serializer):
    file = serializers.FileField()
    mode = serializers.ChoiceField(choices=["validate", "create"], default="validate")

    def validate_file(self, value):
        return check_file_size_and_extension(value, max_size_mb=10, extensions=[".xlsx", ".xls"])


class OperationImportGroupSerializer(serializers.Serializer):
    operation_id = serializers.IntegerField(allow_null=True)
    status = serializers.CharField()
    type = serializers.CharField()
    sector = serializers.CharField()
    customs_category = serializers.CharField()
    biofuel = serializers.CharField()
    debited_entity = OperationEntitySerializer()
    credited_entity = OperationEntitySerializer(allow_null=True)
    lot_count = serializers.IntegerField()
    total_volume = serializers.FloatField()
    rows = serializers.ListField(child=serializers.IntegerField())
    debt = OperationDebtSerializer(allow_null=True)


class OperationImportResponseSerializer(serializers.Serializer):
    mode = serializers.ChoiceField(choices=["validate", "create"])
    operations = OperationImportGroupSerializer(many=True)


class OperationExcelRowSerializer(serializers.Serializer):
    # lot_id/credited_entity are resolved from a cache (see OperationExcelImportService._build_lookup_caches)
    # passed via the serializer context, to avoid one DB query per row when validating with many=True.
    lot_id = CachedPrimaryKeyRelatedField(
        queryset=CarbureLot.objects.select_related("biofuel", "feedstock"),
        cache_key="lot_cache",
        error_messages={"does_not_exist": _("Id de lot invalide")},
    )
    volume = serializers.FloatField()
    operation_type = serializers.CharField()
    credited_entity = CachedPrimaryKeyRelatedField(
        queryset=get_tiruert_operator_queryset(),
        cache_key="credited_entity_cache",
        required=False,
        allow_null=True,
        error_messages={"does_not_exist": _("Destinataire inconu")},
    )
    # Biofuel and category booked in the ledger: they can differ from the lot's own (e.g. EMHV lot booked as EMAG).
    biofuel = serializers.CharField()
    customs_category = serializers.ChoiceField(choices=MatierePremiere.MP_CATEGORIES)

    def validate_biofuel(self, value):
        cache = self.context.get("biofuel_cache")
        biofuel = cache.get(value) if cache is not None else Biocarburant.objects.filter(code=value).first()
        if biofuel is None:
            raise serializers.ValidationError(_("Biocarburant inconnu"))
        return biofuel

    def validate_volume(self, value):
        if value <= 0:
            raise serializers.ValidationError(_("La valeur du volume doit être supérieure à zéro."))
        return value

    def validate_operation_type(self, value):
        normalized = str(value or "").strip().upper()
        if normalized not in [Operation.TRANSFERT, Operation.TENEUR, Operation.DEBT_REPAYMENT]:
            raise serializers.ValidationError(_("Le type d'opération doit être 'TRANSFERT', 'TENEUR' ou 'DEBT_REPAYMENT'."))
        return normalized

    def validate(self, attrs):
        if attrs.get("operation_type") == Operation.TRANSFERT and not attrs.get("credited_entity"):
            raise serializers.ValidationError(
                {"credited_entity": _("Destinataire requis pour les opérations de type TRANSFERT.")}
            )
        # A recipient would split the repayment rows into several groups, each checked against the same debts
        if attrs.get("operation_type") == Operation.DEBT_REPAYMENT and attrs.get("credited_entity"):
            raise serializers.ValidationError(
                {"credited_entity": _("Le destinataire doit rester vide pour les opérations de type DEBT_REPAYMENT.")}
            )
        return attrs


class OperationInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = [
            "type",
            "customs_category",
            "biofuel",
            "credited_entity",
            "debited_entity",
            "from_depot",
            "to_depot",
            "export_country",
            "export_recipient",
            "objective_sector",
            "lots",
            "status",
            "devaluation_type",
        ]
        extra_kwargs = {
            "biofuel": {"required": True, "allow_null": False},
            "customs_category": {"required": True, "allow_null": False},
            "debited_entity": {"required": True, "allow_null": False},
        }

    export_country = serializers.SlugRelatedField(
        slug_field="code_pays", queryset=Pays.objects.all(), required=False, allow_null=True
    )
    lots = OperationLotSerializer(many=True, required=True, allow_empty=False)

    def validate_type(self, value):
        if value not in Operation.API_CREATABLE_TYPES:
            raise serializers.ValidationError("error : OPERATION_TYPE_NOT_AUTHORIZED")
        return value

    def validate(self, data):
        if data.get("credited_entity") and data.get("type") not in (Operation.CESSION, Operation.TRANSFERT):
            raise serializers.ValidationError(
                {"credited_entity": _("Ce champ est autorisé uniquement pour les opérations de type CESSION ou TRANSFERT.")}
            )
        if data.get("objective_sector") and data.get("type") != Operation.TENEUR:
            raise serializers.ValidationError(
                {"declared_sector": "objective_sector ne peut être défini que pour les opérations de type TENEUR"}
            )
        return data

    def create(self, validated_data):
        request = self.context.get("request")
        selected_lots = validated_data.pop("lots")
        operations = OperationService.create_operations(
            request, validated_data, selected_lots, self.context.get("declaration_year")
        )
        return operations if validated_data["type"] == Operation.DEBT_REPAYMENT else operations[0]


class OperationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = ["to_depot", "status"]

    def validate_status(self, value):
        request = self.context.get("request")
        entity_id = getattr(getattr(request, "entity", None), "id", None)
        if self.instance is None or entity_id != self.instance.debited_entity_id:
            raise serializers.ValidationError(_("Seule l'entité débitée peut modifier le statut de l'opération."))

        allowed_transition = {
            Operation.TRANSFERT: (Operation.DRAFT, Operation.PENDING),
            Operation.DEBT_REPAYMENT: (Operation.DRAFT, Operation.VALIDATED),
        }.get(self.instance.type)
        if allowed_transition != (self.instance.status, value):
            raise serializers.ValidationError(_("Le statut de cette opération ne peut pas être modifié via cette action."))
        return value


class OperationCorrectionSerializer(serializers.Serializer):
    correction_volume = serializers.FloatField()

    def update(self, operation, validated_data):
        with transaction.atomic():
            correction_volume = validated_data["correction_volume"]
            debit = correction_volume < 0
            credit = not debit

            # New operation which carry the new lots with the correction volume
            correction = Operation.objects.create(
                type=Operation.CUSTOMS_CORRECTION,
                status=Operation.VALIDATED,
                customs_category=operation.customs_category,
                biofuel=operation.biofuel,
                from_depot=operation.to_depot if debit else None,
                to_depot=operation.to_depot if credit else None,
                debited_entity=operation.credited_entity if debit else None,
                credited_entity=operation.credited_entity if credit else None,
                validation_date=datetime.now(),
            )

            # If the correction volume is positive, we add volume to the first lot id of the operation
            if correction_volume > 0:
                first_lot = operation.details.first()
                OperationDetail.objects.create(
                    operation=correction,
                    lot_id=first_lot.lot_id,
                    volume=abs(correction_volume),
                    emission_rate_per_mj=first_lot.emission_rate_per_mj,  # gCO2/MJ
                )
            # If the correction volume is negative
            # We first need to check if the correction volume is greater than the operation volume
            # Then we empty each lot of the operation until the correction volume is reached
            else:
                if operation.volume < abs(correction_volume):
                    raise serializers.ValidationError({"error": "NOT_ENOUGH_VOLUME"})

                for lot in operation.details.all():
                    if correction_volume == 0:
                        break
                    if lot.volume < abs(correction_volume):
                        correction_volume += lot.volume
                        new_lot_volume = lot.volume
                    else:
                        new_lot_volume = abs(correction_volume)
                        correction_volume = 0

                    OperationDetail.objects.create(
                        operation=correction,
                        lot_id=lot.lot_id,
                        volume=new_lot_volume,
                        emission_rate_per_mj=lot.emission_rate_per_mj,  # gCO2/MJ
                    )
        return correction
