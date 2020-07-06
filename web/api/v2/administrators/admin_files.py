import datetime
import io

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from core.decorators import enrich_with_user_details, restrict_to_administrators

from core.models import LotTransaction


@login_required
@enrich_with_user_details
@restrict_to_administrators
def export_histo(request, *args, **kwargs):
    context = kwargs['context']
    today = datetime.datetime.now()
    filename = 'export_histo_%s.csv' % (today.strftime('%Y%m%d_%H%M%S'))

    transactions = LotTransaction.objects.filter(carbure_vendor=context['user_entity'], lot__status='Validated')
    buffer = io.BytesIO()
    header = "carbure_id;producer;production_site;production_site_country;production_site_reference;production_site_commissioning_date;double_counting_registration;volume;biocarburant_code;\
              matiere_premiere_code;pays_origine_code;eec;el;ep;etd;eu;esca;eccs;eccr;eee;e;dae;champ_libre;client;delivery_date;delivery_site;delivery_site_country\n"
    buffer.write(header.encode())
    for tx in transactions:
        lot = tx.lot
        line = [lot.carbure_id,
                lot.carbure_producer.name if lot.carbure_producer else lot.unknown_producer,
                lot.carbure_production_site.name if lot.carbure_production_site else lot.unknown_production_site,
                lot.carbure_production_site.country.code_pays if lot.carbure_production_site and lot.carbure_production_site.country else lot.unknown_production_country.code_pays if lot.unknown_production_country else '',
                lot.unknown_production_site_reference,
                lot.unknown_production_site_com_date,
                lot.unknown_production_site_dbl_counting,
                lot.volume,
                lot.biocarburant.code if lot.biocarburant else '',
                lot.matiere_premiere.code if lot.matiere_premiere else '',
                lot.pays_origine.code_pays if lot.pays_origine else '',
                lot.eec, lot.el, lot.ep, lot.etd, lot.eu, lot.esca,
                lot.eccs, lot.eccr, lot.eee, lot.ghg_total,
                # tx
                tx.dae,
                tx.champ_libre,
                tx.carbure_client.name if tx.client_is_in_carbure else tx.unknown_client,
                tx.delivery_date,
                tx.carbure_delivery_site.depot_id if tx.delivery_site_is_in_carbure else tx.unknown_delivery_site,
                tx.carbure_delivery_site.country.code_pays if tx.delivery_site_is_in_carbure else tx.unknown_delivery_site_country.code_pays if tx.unknown_delivery_site_country else ''
                ]
        csvline = '%s\n' % (';'.join([str(k) for k in line]))
        buffer.write(csvline.encode('iso-8859-1'))
    csvfile = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="%s"' % (filename)
    response.write(csvfile)
    return response
