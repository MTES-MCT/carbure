from biomethane.models import BiomethaneDigestate, BiomethaneEnergy


class BiomethaneAnnualDeclarationService:
    @staticmethod
    def get_missing_fields(declaration):
        digestat_missing_fields = []
        energy_missing_fields = []

        try:
            digestat = BiomethaneDigestate.objects.get(producer=declaration.producer, year=declaration.year)
        except BiomethaneDigestate.DoesNotExist:
            digestat = None

        try:
            energy = BiomethaneEnergy.objects.get(producer=declaration.producer, year=declaration.year)
        except BiomethaneEnergy.DoesNotExist:
            energy = None

        if digestat is not None:
            digestat_missing_fields = BiomethaneAnnualDeclarationService._get_missing_fields(digestat)

        if energy is not None:
            energy_missing_fields = BiomethaneAnnualDeclarationService._get_missing_fields(energy)

        return {
            "digestate_missing_fields": digestat_missing_fields,
            "energy_missing_fields": energy_missing_fields,
        }

    @staticmethod
    def _get_missing_fields(instance):
        """
        Return all missing fields for an instance.
        Takes into account optional fields defined by business rules.
        """
        all_fields = BiomethaneAnnualDeclarationService.get_required_fields(model=type(instance))

        optional_fields = instance.optional_fields if hasattr(instance, "optional_fields") else []
        required_fields = list(set(all_fields) - set(optional_fields))

        missing_fields = []
        for field in required_fields:
            value = getattr(instance, field, None)
            # Missing if None, empty string, or empty list
            if value is None or value == "" or value == []:
                missing_fields.append(field)

        return missing_fields

    @staticmethod
    def get_required_fields(model):
        if model is None:
            return []
        fields = []
        for field in model._meta.get_fields():
            fields.append(field.name)
        return fields

    @staticmethod
    def is_declaration_complete(declaration):
        missing_fields = BiomethaneAnnualDeclarationService.get_missing_fields(declaration)
        return len(missing_fields["digestate_missing_fields"]) == 0 and len(missing_fields["energy_missing_fields"]) == 0
