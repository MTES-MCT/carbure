from django.db import models
from core.models import Entity, Pays
from producers.models import ProductionSite

class SNCategory(models.Model):
    category_id = models.CharField(max_length=6, default='')
    description = models.CharField(max_length=512, default='')

    def natural_key(self):
        return {'category_id': self.category_id}

    def __str__(self):
        return self.category_id

    class Meta:
        db_table = 'sn_categories'
        verbose_name = 'SN Category'
        verbose_name_plural = 'SN Categories'


class SNCertificate(models.Model):
    certificate_id = models.CharField(max_length=64, null=False, blank=False)
    certificate_holder = models.CharField(max_length=256, null=False, blank=False)
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField()
    download_link = models.CharField(max_length=512, default='', blank=True)

    def natural_key(self):
        scope = [s.scope.category_id for s in self.sncertificatescope_set.all()]

        return {'certificate_id': self.certificate_id,
                'certificate_holder': self.certificate_holder,
                'valid_from': self.valid_from,
                'valid_until': self.valid_until,
                'download_link': self.download_link,
                'scope': scope,
                }

    def __str__(self):
        return self.certificate_id

    class Meta:
        db_table = 'sn_certificates'
        verbose_name = 'SN Certificate'
        verbose_name_plural = 'SN Certificates'


class SNCertificateScope(models.Model):
    certificate = models.ForeignKey(SNCertificate, blank=False, null=False, on_delete=models.CASCADE)
    scope = models.ForeignKey(SNCategory, blank=False, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.scope.category_id

    class Meta:
        db_table = 'sn_certificates_scopes'
        verbose_name = 'SN Certificate Scope'
        verbose_name_plural = 'SN Certificate Scopes'

        

class EntitySNTradingCertificate(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    certificate = models.ForeignKey(SNCertificate, on_delete=models.CASCADE)
    has_been_updated = models.BooleanField(default=False)

    def __str__(self):
        return '%s - %s' % (self.entity.name, self.certificate.certificate_id)

    def natural_key(self):
        data = self.certificate.natural_key()
        data['type'] = "SN"
        data['has_been_updated'] = self.has_been_updated
        return data

    class Meta:
        db_table = 'entity_sn_certificates'
        verbose_name = 'Certificat Système National'
        verbose_name_plural = 'Certificats Système National liés à des sociétés'



class ISCCScope(models.Model):
    scope = models.CharField(max_length=8, null=False, blank=False)
    description = models.CharField(max_length=256, null=False, blank=False)

    def __str__(self):
        return self.scope

    class Meta:
        db_table = 'iscc_scopes'
        verbose_name = 'ISCC Scope'
        verbose_name_plural = 'ISCC Scopes'


class ISCCCertificate(models.Model):
    certificate_id = models.CharField(max_length=64, null=False, blank=False)
    # warning, this column must be manually altered in db to support utf8mb4
    # command: ALTER TABLE iscc_certificates CHANGE certificate_holder certificate_holder VARCHAR(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    # do not change anything
    certificate_holder = models.CharField(max_length=256, null=False, blank=False)
    addons = models.CharField(max_length=256, null=False, blank=False)
    valid_from = models.DateField(null=False)
    valid_until = models.DateField(null=False)
    issuing_cb = models.CharField(max_length=256, default='')
    location = models.CharField(max_length=256, default='')
    download_link = models.CharField(max_length=512, default='')

    def natural_key(self):
        scope = [s.scope.scope for s in self.iscccertificatescope_set.all()]

        return {'certificate_id': self.certificate_id,
                'certificate_holder': self.certificate_holder,
                'location': self.location,
                'valid_from': self.valid_from,
                'valid_until': self.valid_until,
                'issuing_cb': self.issuing_cb,
                'download_link': self.download_link,
                'scope': scope}

    def __str__(self):
        return self.certificate_id

    class Meta:
        db_table = 'iscc_certificates'
        verbose_name = 'ISCC Certificate'
        verbose_name_plural = 'ISCC Certificates'


class ISCCCertificateRawMaterial(models.Model):
    certificate = models.ForeignKey(ISCCCertificate, blank=False, null=False, on_delete=models.CASCADE)
    raw_material = models.CharField(max_length=128, blank=False, null=False)
    # add foreign key to MatierePremiere ?

    def __str__(self):
        return self.raw_material

    class Meta:
        db_table = 'iscc_certificates_raw_materials'
        verbose_name = 'ISCC Certificate Raw Material'
        verbose_name_plural = 'ISCC Certificate Raw Materials'


class ISCCCertificateScope(models.Model):
    certificate = models.ForeignKey(ISCCCertificate, blank=False, null=False, on_delete=models.CASCADE)
    scope = models.ForeignKey(ISCCScope, blank=False, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.scope.scope

    class Meta:
        db_table = 'iscc_certificates_scopes'
        verbose_name = 'ISCC Certificate Scope'
        verbose_name_plural = 'ISCC Certificate Scopes'


class DBSScope(models.Model):
    certification_type = models.CharField(max_length=512, default='')

    def natural_key(self):
        return {'certification_type': self.certification_type}

    def __str__(self):
        return self.certification_type

    class Meta:
        db_table = 'dbs_scopes'
        verbose_name = '2BS Scope'
        verbose_name_plural = '2BS Scopes'


class DBSCertificate(models.Model):
    certificate_id = models.CharField(max_length=64, null=False, blank=False)
    certificate_holder = models.CharField(max_length=256, null=False, blank=False)
    # warning, this column must be manually altered in db to support utf8mb4
    # command: ALTER TABLE dbs_certificates CHANGE certificate_holder certificate_holder VARCHAR(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    # command: ALTER TABLE dbs_certificates CHANGE holder_address holder_address VARCHAR(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    # do not change this field
    holder_address = models.CharField(max_length=512, null=False, blank=False)
    valid_from = models.DateField()
    valid_until = models.DateField()
    certification_type = models.CharField(max_length=512, default='')
    download_link = models.CharField(max_length=512, default='')

    def natural_key(self):
        scope = [s.scope.certification_type for s in self.dbscertificatescope_set.all()]
        return {'certificate_id': self.certificate_id,
                'certificate_holder': self.certificate_holder,
                'holder_address': self.holder_address,
                'valid_from': self.valid_from,
                'valid_until': self.valid_until,
                'certification_type': self.certification_type,
                'download_link': self.download_link,
                'scope': scope}

    def __str__(self):
        return self.certificate_id

    class Meta:
        db_table = 'dbs_certificates'
        verbose_name = '2BS Certificate'
        verbose_name_plural = '2BS Certificates'


class DBSCertificateScope(models.Model):
    certificate = models.ForeignKey(DBSCertificate, blank=False, null=False, on_delete=models.CASCADE)
    scope = models.ForeignKey(DBSScope, blank=False, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.scope.scope

    class Meta:
        db_table = 'dbs_certificates_scopes'
        verbose_name = '2BS Certificate Scope'
        verbose_name_plural = '2BS Certificate Scopes'


class REDCertScope(models.Model):
    scope = models.CharField(max_length=8, null=False, blank=False)
    description_fr = models.CharField(max_length=256, null=False, blank=False)
    description_en = models.CharField(max_length=256, null=False, blank=False)
    description_de = models.CharField(max_length=256, null=False, blank=False)

    def __str__(self):
        return self.scope

    class Meta:
        db_table = 'redcert_scopes'
        verbose_name = 'REDCert Scope'
        verbose_name_plural = 'REDCert Scopes'


class REDCertBiomassType(models.Model):
    code = models.CharField(max_length=16, null=False, blank=False)
    description_fr = models.CharField(max_length=256, null=False, blank=False)
    description_en = models.CharField(max_length=256, null=False, blank=False)
    description_de = models.CharField(max_length=256, null=False, blank=False)

    def __str__(self):
        return self.code

    class Meta:
        db_table = 'redcert_biomass_types'
        verbose_name = 'REDCert Biomass Type'
        verbose_name_plural = 'REDCert Biomass Types'


class REDCertCertificate(models.Model):
    certificate_id = models.CharField(max_length=64, null=False, blank=False)
    certificate_holder = models.CharField(max_length=256, null=False, blank=False)
    city = models.CharField(max_length=256, default='')
    zip_code = models.CharField(max_length=12, default='')
    country_raw = models.CharField(max_length=32, default='')
    country = models.ForeignKey(Pays, on_delete=models.SET_NULL, blank=True, null=True)
    valid_from = models.DateField(null=False)
    valid_until = models.DateField(null=False)
    certificator = models.CharField(max_length=256, default='')
    certificate_type = models.CharField(max_length=256, default='')
    status = models.CharField(max_length=32, default='')

    def natural_key(self):
        scope = [s.scope.scope for s in self.redcertcertificatescope_set.all()]
        return {'certificate_id': self.certificate_id,
                'certificate_holder': self.certificate_holder,
                'city': self.city,
                'zip_code': self.zip_code,
                'country': self.country.natural_key() if self.country else '',
                'country_raw': self.country_raw,
                'valid_from': self.valid_from,
                'valid_until': self.valid_until,
                'certificator': self.certificator,
                'certificate_type': self.certificate_type,
                'scope': scope,
                'status': self.status}

    def __str__(self):
        return self.certificate_id

    class Meta:
        db_table = 'redcert_certificates'
        verbose_name = 'REDCert Certificate'
        verbose_name_plural = 'REDCert Certificates'


class REDCertCertificateScope(models.Model):
    certificate = models.ForeignKey(REDCertCertificate, blank=False, null=False, on_delete=models.CASCADE)
    scope = models.ForeignKey(REDCertScope, blank=False, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.scope.scope

    class Meta:
        db_table = 'redcert_certificates_scopes'
        verbose_name = 'REDCert Certificate Scope'
        verbose_name_plural = 'REDCert Certificate Scopes'


class REDCertCertificateBiomass(models.Model):
    certificate = models.ForeignKey(REDCertCertificate, blank=False, null=False, on_delete=models.CASCADE)
    biomass = models.ForeignKey(REDCertBiomassType, blank=False, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.biomass.code

    class Meta:
        db_table = 'redcert_certificates_biomass'
        verbose_name = 'REDCert Certificate Biomass'
        verbose_name_plural = 'REDCert Certificate Biomass'


from certificates.models import ISCCCertificate

class EntityISCCTradingCertificate(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    certificate = models.ForeignKey(ISCCCertificate, on_delete=models.CASCADE)
    has_been_updated = models.BooleanField(default=False)

    def __str__(self):
        return '%s - %s' % (self.entity.name, self.certificate.certificate_id)

    def natural_key(self):
        data = self.certificate.natural_key()
        data['type'] = "ISCC"
        data['has_been_updated'] = self.has_been_updated
        return data

    class Meta:
        db_table = 'entity_iscc_trading_certificates'
        verbose_name = 'Certificat de Trading ISCC'
        verbose_name_plural = 'Certificats de Trading ISCC'


class EntityDBSTradingCertificate(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    certificate = models.ForeignKey(DBSCertificate, on_delete=models.CASCADE)
    has_been_updated = models.BooleanField(default=False)

    def __str__(self):
        return '%s - %s' % (self.entity.name, self.certificate.certificate_id)

    def natural_key(self):
        data = self.certificate.natural_key()
        data['type'] = "2BS"
        data['has_been_updated'] = self.has_been_updated
        return data

    class Meta:
        db_table = 'entity_2bs_trading_certificates'
        verbose_name = 'Certificat de Trading 2BS'
        verbose_name_plural = 'Certificats de Trading 2BS'


class EntityREDCertTradingCertificate(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    certificate = models.ForeignKey(REDCertCertificate, on_delete=models.CASCADE)
    has_been_updated = models.BooleanField(default=False)

    def __str__(self):
        return '%s - %s' % (self.entity.name, self.certificate.certificate_id)

    def natural_key(self):
        data = self.certificate.natural_key()
        data['type'] = "REDCERT"
        data['has_been_updated'] = self.has_been_updated
        return data

    class Meta:
        db_table = 'entity_redcert_trading_certificates'
        verbose_name = 'Certificat de Trading REDCert'
        verbose_name_plural = 'Certificats de Trading REDCert'


class ProductionSiteCertificate(models.Model):
    CERTIFICATE_TYPE = [("ISCC", "ISCC"), ("2BS", "2BS"), ('REDCERT', 'REDCERT'), ('SN', 'SN')]
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    production_site = models.ForeignKey(ProductionSite, null=True, on_delete=models.CASCADE)
    type = models.CharField(max_length=32, choices=CERTIFICATE_TYPE, default="Pending")

    certificate_iscc = models.ForeignKey(EntityISCCTradingCertificate, null=True, blank=True, on_delete=models.CASCADE)
    certificate_2bs = models.ForeignKey(EntityDBSTradingCertificate, null=True, blank=True, on_delete=models.CASCADE)
    certificate_redcert = models.ForeignKey(EntityREDCertTradingCertificate, null=True, blank=True, on_delete=models.CASCADE)
    certificate_sn = models.ForeignKey("certificates.EntitySNTradingCertificate", null=True, blank=True, on_delete=models.CASCADE)

    def natural_key(self):
        if self.type == 'ISCC':
            cert = self.certificate_iscc
        elif self.type == '2BS':
            cert = self.certificate_2bs
        elif self.type == 'REDCERT':
            cert = self.certificate_redcert
        else:
            cert = self.certificate_sn
        return {'type': self.type, 'certificate_id': cert.certificate.certificate_id}

    class Meta:
        db_table = 'production_sites_certificates'
        verbose_name = 'Certificat de site de production'
        verbose_name_plural = 'Certificats de sites de productions'
