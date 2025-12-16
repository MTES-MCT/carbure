from django import forms
from django.contrib import admin

from core.models import Department, Entity
from entity.models import EntityScopeDepartment, EntityScopeDepot
from entity.services.enable_entity import enable_entity
from transactions.models import Depot


class EntityDepartmentForm(forms.ModelForm):
    """Custom form for selecting departments in EntityScope"""

    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=True,
        label="Département",
    )

    class Meta:
        model = EntityScopeDepartment
        fields = ["department"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.content_object:
            # Populate department field from content_object
            self.fields["department"].initial = self.instance.content_object

    def save(self, commit=True):
        from django.contrib.contenttypes.models import ContentType

        instance = super().save(commit=False)
        dept = self.cleaned_data.get("department")
        if dept:
            instance.content_type = ContentType.objects.get_for_model(Department)
            instance.object_id = dept.id
        if commit:
            instance.save()
        return instance


class EntityDepotForm(forms.ModelForm):
    """Custom form for selecting depots in EntityScope"""

    depot = forms.ModelChoiceField(
        queryset=Depot.objects.all(),
        required=True,
        label="Dépôt",
    )

    class Meta:
        model = EntityScopeDepot
        fields = ["depot"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.content_object:
            # Populate depot field from content_object
            self.fields["depot"].initial = self.instance.content_object

    def save(self, commit=True):
        from django.contrib.contenttypes.models import ContentType

        instance = super().save(commit=False)
        depot = self.cleaned_data.get("depot")
        if depot:
            instance.content_type = ContentType.objects.get_for_model(Depot)
            instance.object_id = depot.id
        if commit:
            instance.save()
        return instance


class EntityDepartmentInline(admin.TabularInline):
    """Inline admin to manage departments accessible by entities (e.g., DREAL)"""

    model = EntityScopeDepartment
    form = EntityDepartmentForm
    extra = 1
    verbose_name = "Département accessible"
    verbose_name_plural = "Départements accessibles"


class EntityDepotInline(admin.TabularInline):
    """Inline admin to manage depots accessible by entities"""

    model = EntityScopeDepot
    form = EntityDepotForm
    extra = 1
    verbose_name = "Dépôt accessible"
    verbose_name_plural = "Dépôts accessibles"


class EntityAdmin(admin.ModelAdmin):
    list_display = (
        "entity_type",
        "name",
        "parent_entity",
        "is_enabled",
    )
    search_fields = ("entity_type", "name")
    list_filter = ["entity_type"]
    readonly_fields = ["is_enabled"]
    inlines = [EntityDepartmentInline, EntityDepotInline]

    actions = ["enable_entity"]

    def enable_entity(self, request, queryset):
        for entity in queryset:
            enable_entity(entity, request)

    enable_entity.short_description = "Activer les sociétés sélectionnées"


admin.site.register(Entity, EntityAdmin)
