from types import SimpleNamespace
from unittest.mock import Mock

from django.test import SimpleTestCase
from rest_framework import serializers

from traceability.serializers.fields import LookupSlugRelatedField
from traceability.serializers.lookups import CertificateLookupField, MaterialLookupField, SiteLookupField


class LookupSlugRelatedFieldTest(SimpleTestCase):
    def test_declarative_fields_resolve_relations(self):
        for field_class, lookup, instance, value in (
            (MaterialLookupField, "material", SimpleNamespace(name="Hydrogène gazeux"), "Hydrogène gazeux"),
            (CertificateLookupField, "certificate", SimpleNamespace(certificate_id="CHY-001"), "CHY-001"),
            (SiteLookupField, "site", SimpleNamespace(name="Station Paris"), "Station Paris"),
        ):
            with self.subTest(field=field_class.__name__):
                entity = object()
                get_queryset = Mock(return_value=[instance])
                context = {"handler": SimpleNamespace(lookups=SimpleNamespace(**{lookup: get_queryset})), "entity": entity}
                field = field_class()
                field.bind("relation", serializers.Serializer(context=context))

                self.assertIs(field.run_validation(value), instance)
                get_queryset.assert_called_once_with(entity)

    def test_constructor_arguments_override_inherited_class_attributes(self):
        class InheritedMaterialLookupField(MaterialLookupField):
            pass

        site = SimpleNamespace(code="SITE-001")
        get_sites = Mock(return_value=[site])
        context = {"handler": SimpleNamespace(lookups=SimpleNamespace(site=get_sites))}
        field = InheritedMaterialLookupField(slug_field="code", lookup="site")
        field.bind("relation", serializers.Serializer(context=context))

        self.assertIs(field.run_validation("SITE-001"), site)
        get_sites.assert_called_once_with(None)

    def test_accepts_positional_slug_field(self):
        material = SimpleNamespace(name="H2")
        field = LookupSlugRelatedField("name", lookup="material")
        field.bind("relation", serializers.Serializer(context={"serializer_cache": {"material": {"H2": material}}}))

        self.assertIs(field.run_validation("H2"), material)

    def test_get_queryset_is_called_once_when_context_is_shared(self):
        material = SimpleNamespace(name="Hydrogène gazeux")
        context = {}

        first = LookupSlugRelatedField(slug_field="name", lookup="material")
        second = LookupSlugRelatedField(slug_field="name", lookup="material")
        first._context = context
        second._context = context
        first.get_queryset = Mock(return_value=[material])
        second.get_queryset = Mock(return_value=[material])

        self.assertEqual(first.to_internal_value("Hydrogène gazeux"), material)
        self.assertEqual(second.to_internal_value("Hydrogène gazeux"), material)
        first.get_queryset.assert_called_once()
        second.get_queryset.assert_not_called()
