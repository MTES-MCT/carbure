from rest_framework import serializers
from .models import DoubleCountingAgreement

class DoubleCountingAgreementFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoubleCountingAgreement
        fields = ['producer', 'production_site', 'period_start', 'period_end', 'status', 'dgec_validated', 'dgec_validator', 'dgec_validated_dt', 'dgddi_validated', 'dgddi_validator', 'dgddi_validated_dt', 'dgpe_validated', 'dgpe_validator', 'dgpe_validated_dt']

class DoubleCountingAgreementPartialSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoubleCountingAgreement
        fields = ['producer', 'production_site', 'period_start', 'period_end', 'status']
        
