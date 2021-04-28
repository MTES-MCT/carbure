from django.contrib import admin

from certificates.models import SNCategory, SNCertificate, SNCertificateScope
from certificates.models import ISCCScope, ISCCCertificateRawMaterial, ISCCCertificate, ISCCCertificateScope
from certificates.models import DBSCertificate, DBSScope, DBSCertificateScope
from certificates.models import REDCertScope, REDCertBiomassType, REDCertCertificate, REDCertCertificateScope, REDCertCertificateBiomass
from certificates.models import ProductionSiteCertificate, EntityISCCTradingCertificate, EntitySNTradingCertificate, EntityDBSTradingCertificate, EntityREDCertTradingCertificate

class SNCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'description',)


class SNCertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'get_scopes', 'certificate_holder', 'valid_until', )
    search_fields = ('certificate_holder', 'certificate_id',)
    list_filter = ('sncertificatescope', )


    def get_scopes(self, obj):
        scopes = obj.sncertificatescope_set.all()
        scopes = [s.scope.category_id for s in scopes]
        return '&'.join(scopes)
    get_scopes.short_description = 'Scope'


class SNCertificateScopeAdmin(admin.ModelAdmin):
    list_display = ('certificate', 'scope',)


class EntitySNTradingCertificateAdmin(admin.ModelAdmin):
    list_display = ('entity', 'certificate',)
    search_fields = ('entity', 'certificate',)


class ISCCScopeAdmin(admin.ModelAdmin):
    list_display = ('scope', 'description')
    search_fields = ('scope', 'description')


class ISCCCertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'certificate_holder', 'valid_from', 'valid_until')
    search_fields = ('certificate_id', 'certificate_holder', 'issuing_cb')


class ISCCCertificateRawMaterialAdmin(admin.ModelAdmin):
    list_display = ('certificate', 'raw_material')
    search_fields = ('certificate__certificate_id', 'raw_material')
    raw_id_fields = ('certificate', )


class ISCCCertificateScopeAdmin(admin.ModelAdmin):
    list_display = ('certificate', 'scope')
    search_fields = ('certificate__certificate_id', 'certificate__certificate_holder', 'scope__scope')
    raw_id_fields = ('certificate', )


class DBSScopeAdmin(admin.ModelAdmin):
    list_display = ('certification_type', )
    search_fields = ('certification_type', )


class DBSCertificateScopeAdmin(admin.ModelAdmin):
    list_display = ('certificate', 'scope')
    search_fields = ('certificate', 'scope')
    raw_id_fields = ('certificate', )


class DBSCertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'certificate_holder', 'holder_address', 'valid_from', 'valid_until')
    search_fields = ('certificate_id', 'certificate_holder', 'holder_address')


class REDCertScopeAdmin(admin.ModelAdmin):
    list_display = ('scope', 'description_fr', 'description_de', 'description_en')
    search_fields = ('scope', 'description_fr', 'description_de', 'description_en')


class REDCertBiomassTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'description_fr', 'description_de', 'description_en')
    search_fields = ('code', 'description_fr', 'description_de', 'description_en')


class REDCertCertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'certificate_holder', 'city', 'country', 'valid_from', 'valid_until', 'certificator', 'certificate_type', 'status')
    search_fields = ('certificate_id', 'certificate_holder', 'city', 'certificator', 'certificate_type')
    list_filter = ('country', 'status', 'certificate_type')


class REDCertCertificateScopeAdmin(admin.ModelAdmin):
    list_display = ('certificate', 'scope')
    search_fields = ('certificate__certificate_id',)
    list_filter = ('scope', )


class REDCertCertificateBiomassAdmin(admin.ModelAdmin):
    list_display = ('certificate', 'biomass')
    search_fields = ('certificate', 'biomass')
    list_filter = ('biomass', )


class EntityISCCTradingCertificateAdmin(admin.ModelAdmin):
    list_display = ('entity', 'certificate',)
    search_fields = ('entity', 'certificate',)


class EntityDBSTradingCertificateAdmin(admin.ModelAdmin):
    list_display = ('entity', 'certificate',)
    search_fields = ('entity', 'certificate',)


class EntityREDCertTradingCertificateAdmin(admin.ModelAdmin):
    list_display = ('entity', 'certificate',)
    search_fields = ('entity', 'certificate',)


class ProductionSiteCertificateAdmin(admin.ModelAdmin):
    list_display = ('production_site', 'type', 'certificate_iscc', 'certificate_2bs', 'certificate_redcert')
    search_fields = ('production_site', 'certificate_iscc', 'certificate_2bs', 'certificate_redcert')
    list_filter = ('type',)
    

admin.site.register(SNCategory, SNCategoryAdmin)
admin.site.register(SNCertificate, SNCertificateAdmin)
admin.site.register(SNCertificateScope, SNCertificateScopeAdmin)

admin.site.register(ISCCScope, ISCCScopeAdmin)
admin.site.register(ISCCCertificate, ISCCCertificateAdmin)
admin.site.register(ISCCCertificateRawMaterial, ISCCCertificateRawMaterialAdmin)
admin.site.register(ISCCCertificateScope, ISCCCertificateScopeAdmin)

admin.site.register(DBSCertificate, DBSCertificateAdmin)
admin.site.register(DBSScope, DBSScopeAdmin)
admin.site.register(DBSCertificateScope, DBSCertificateScopeAdmin)

admin.site.register(REDCertCertificate, REDCertCertificateAdmin)
admin.site.register(REDCertScope, REDCertScopeAdmin)
admin.site.register(REDCertBiomassType, REDCertBiomassTypeAdmin)
admin.site.register(REDCertCertificateScope, REDCertCertificateScopeAdmin)
admin.site.register(REDCertCertificateBiomass, REDCertCertificateBiomassAdmin)

admin.site.register(EntitySNTradingCertificate, EntitySNTradingCertificateAdmin)
admin.site.register(EntityISCCTradingCertificate, EntityISCCTradingCertificateAdmin)
admin.site.register(EntityDBSTradingCertificate, EntityDBSTradingCertificateAdmin)
admin.site.register(EntityREDCertTradingCertificate, EntityREDCertTradingCertificateAdmin)
admin.site.register(ProductionSiteCertificate, ProductionSiteCertificateAdmin)    