from rest_framework import serializers

from stock_poc.serializers.action import ActionSerializer


class QueryScenarioSerializer(serializers.Serializer):
    name = serializers.CharField()
    help = serializers.CharField()
    requires_entity = serializers.BooleanField()
    entity_id = serializers.IntegerField(allow_null=True)
    results = ActionSerializer(many=True)


class QueryScenariosResponseSerializer(serializers.Serializer):
    query_entity_id = serializers.IntegerField(allow_null=True)
    scenarios = QueryScenarioSerializer(many=True)
