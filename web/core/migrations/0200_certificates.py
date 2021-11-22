import datetime
from django.db import connection, migrations

from certificates.models import EntitySNTradingCertificate, SNCertificate
from certificates.models import EntityISCCTradingCertificate, ISCCCertificate
from certificates.models import EntityREDCertTradingCertificate, REDCertCertificate
from certificates.models import EntityDBSTradingCertificate, DBSCertificate
from core.models import GenericCertificate, EntityCertificate

def alter_column(apps, schema_editor):
    cursor = connection.cursor()
    sql1 = "ALTER TABLE carbure_certificates CHANGE certificate_holder certificate_holder VARCHAR(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    cursor.execute(sql1)
    sql2 = "ALTER TABLE carbure_certificates CHANGE address address VARCHAR(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    cursor.execute(sql2)


def migrate_certitifates(apps, schema_editor):
    # SN
    sn = SNCertificate.objects.all()
    sne = EntitySNTradingCertificate.objects.all()
    for s in sn:
        print(s.certificate_id)
        year_from = s.certificate_id.split('_')[2]
        dt_from = datetime.date(year=int(year_from), month=1, day=1)

        d = {'certificate_type': GenericCertificate.SYSTEME_NATIONAL,
             'certificate_holder': s.certificate_holder,
             'valid_from': s.valid_from if s.valid_from else dt_from,
             'valid_until': s.valid_until,
             'download_link': s.download_link,}
        GenericCertificate.objects.update_or_create(certificate_id=s.certificate_id, defaults=d)
    for se in sne:
        cert = GenericCertificate.objects.filter(certificate_id=se.certificate.certificate_id)
        if cert.count() > 0:
            EntityCertificate.objects.update_or_create(certificate=cert[0], entity=se.entity)
        else:
            print('Could not migrate certificate %s' % (se.certificate.certificate_id))

    # ISCC
    certs = ISCCCertificate.objects.all()
    iscc_links = EntityISCCTradingCertificate.objects.all()
    for c in certs:
        print(c.certificate_id)
        d = {'certificate_type': GenericCertificate.ISCC,
             'certificate_holder': c.certificate_holder,
             'certificate_issuer': c.issuing_cb,
             'address': c.location,
             'valid_from': c.valid_from,
             'valid_until': c.valid_until,
             'download_link': c.download_link,}
        GenericCertificate.objects.update_or_create(certificate_id=c.certificate_id, defaults=d)
    for link in iscc_links:
        cert = GenericCertificate.objects.filter(certificate_type=GenericCertificate.ISCC, certificate_id=link.certificate.certificate_id)
        if cert.count() > 0:
            EntityCertificate.objects.update_or_create(certificate=cert[0], entity=link.entity)
        else:
            print('Could not migrate certificate %s' % (link.certificate.certificate_id))        
    # REDCERT
    certs = REDCertCertificate.objects.all()
    red_links = EntityREDCertTradingCertificate.objects.all()
    for c in certs:
        print(c.certificate_id)
        d = {'certificate_type': GenericCertificate.REDCERT,
             'certificate_holder': c.certificate_holder,
             'certificate_issuer': c.certificator,
             'address': "%s %s %s" % (c.city, c.zip_code, c.country_raw),
             'valid_from': c.valid_from,
             'valid_until': c.valid_until,
             'download_link': None}
        GenericCertificate.objects.update_or_create(certificate_id=c.certificate_id, defaults=d)
    for link in red_links:
        cert = GenericCertificate.objects.filter(certificate_type=GenericCertificate.REDCERT, certificate_id=link.certificate.certificate_id)
        if cert.count() > 0:
            EntityCertificate.objects.update_or_create(certificate=cert[0], entity=link.entity)
        else:
            print('Could not migrate certificate %s' % (link.certificate.certificate_id))   
    # 2BS
    certs = DBSCertificate.objects.all()
    dbs_links = EntityDBSTradingCertificate.objects.all()
    for c in certs:
        print(c.certificate_id)
        d = {'certificate_type': GenericCertificate.DBS,
             'certificate_holder': c.certificate_holder,
             'certificate_issuer': None,
             'address': c.holder_address,
             'valid_from': c.valid_from,
             'valid_until': c.valid_until,
             'download_link': c.download_link,}
        GenericCertificate.objects.update_or_create(certificate_id=c.certificate_id, defaults=d)
    for link in dbs_links:
        cert = GenericCertificate.objects.filter(certificate_type=GenericCertificate.DBS, certificate_id=link.certificate.certificate_id)
        if cert.count() > 0:
            EntityCertificate.objects.update_or_create(certificate=cert[0], entity=link.entity)
        else:
            print('Could not migrate certificate %s' % (link.certificate.certificate_id))   



class Migration(migrations.Migration):

    dependencies = [
        ('core', '0199_alter_genericcertificate_address'),
    ]

    operations = [
        migrations.RunPython(alter_column, migrations.RunPython.noop),
        migrations.RunPython(migrate_certitifates, migrations.RunPython.noop),
    ]
