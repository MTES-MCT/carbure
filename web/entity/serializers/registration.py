from rest_framework import serializers


class SeachCompanySerializer(serializers.Serializer):
    registration_id = serializers.CharField(required=True)  # SIREN
    siret = serializers.BooleanField(required=False, default=False)

    def validate_registration_id(self, value):
        siret = self.initial_data.get("siret", False)

        if siret and len(value) != 14:
            raise serializers.ValidationError("Le numéro SIRET doit être de 14 caractères")
        elif not siret and len(value) != 9:
            raise serializers.ValidationError("Le numéro SIREN doit être de 9 caractères")
        return value


class RegistrationCountrySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    name_en = serializers.CharField(max_length=255)
    code_pays = serializers.CharField(max_length=10)
    is_in_europe = serializers.BooleanField()


class CompanyPreviewSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    legal_name = serializers.CharField(max_length=255)
    registration_id = serializers.CharField(max_length=50)
    registered_address = serializers.CharField(max_length=500)
    registered_city = serializers.CharField(max_length=255)
    registered_zipcode = serializers.CharField(max_length=20)
    registered_country = RegistrationCountrySerializer()


class WarningSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    meta = serializers.DictField()


class ResponseDataSerializer(serializers.Serializer):
    company_preview = CompanyPreviewSerializer()
    warning = WarningSerializer(required=False)
