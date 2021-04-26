from django.contrib import admin

from certificates.models import SNCategory, SNCertificate, SNCertificateScope, EntitySNTradingCertificate


class SNCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'description',)

admin.site.register(SNCategory, SNCategoryAdmin)



class SNCertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'get_scopes', 'certificate_holder', 'valid_until', )
    search_fields = ('certificate_holder', 'certificate_id',)
    list_filter = ('sncertificatescope', )


    def get_scopes(self, obj):
        scopes = obj.sncertificatescope_set.all()
        scopes = [s.scope.category_id for s in scopes]
        return '&'.join(scopes)
    get_scopes.short_description = 'Scope'


admin.site.register(SNCertificate, SNCertificateAdmin)


class SNCertificateScopeAdmin(admin.ModelAdmin):
    list_display = ('certificate', 'scope',)

admin.site.register(SNCertificateScope, SNCertificateScopeAdmin)


class EntitySNTradingCertificateAdmin(admin.ModelAdmin):
    list_display = ('entity', 'certificate',)
    search_fields = ('entity', 'certificate',)

admin.site.register(EntitySNTradingCertificate, EntitySNTradingCertificateAdmin)
