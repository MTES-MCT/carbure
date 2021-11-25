import api, { Api } from 'common-v2/services/api'
import { Lot } from 'transactions-v2/types'
import { LotFormValue } from './components/lot-form'
import { LotPayload } from './types'

export function addLot(entity_id: number, lot: LotFormValue) {
  return api.post<Api<Lot>>('/lots/add', { entity_id, ...lotFormToPayload(lot) })
}

export function lotFormToPayload(lot: LotFormValue): LotPayload {
  return {
    transport_document_type: undefined,
    transport_document_reference: lot.transport_document_reference,
    volume: lot.volume,
    biofuel_code: lot.biofuel?.code,
    feedstock_code: lot.feedstock?.code,
    country_code: lot.country_of_origin?.code_pays,
    free_field: lot.free_field,

    eec: lot.eec,
    el: lot.el,
    ep: lot.ep,
    etd: lot.etd,
    eu: lot.eu,
    esca: lot.esca,
    eccs: lot.eccs,
    eccr: lot.eccr,
    eee: lot.eee,

    // production
    carbure_producer_id: lot.producer instanceof Object ? lot.producer.id : undefined,
    unknown_producer: typeof lot.producer === 'string' ? lot.producer : undefined,
    carbure_production_site_id: lot.production_site instanceof Object ? lot.production_site.id : undefined,
    unknown_production_site: typeof lot.production_site === 'string' ? lot.production_site : undefined,
    production_site_certificate: lot.production_site_certificate,
    production_site_certificate_type: undefined,
    production_country_code: lot.production_country?.code_pays,
    production_site_commissioning_date: lot.production_site_commissioning_date,
    production_site_double_counting_certificate: lot.production_site_double_counting_certificate,

    // supplier
    carbure_supplier_id: lot.supplier instanceof Object ? lot.supplier.id : undefined,
    unknown_supplier: typeof lot.supplier === 'string' ? lot.supplier : undefined,
    supplier_certificate: lot.supplier_certificate,
    supplier_certificate_type: undefined,

    // delivery
    delivery_date: lot.delivery_date,
    carbure_client_id: lot.client instanceof Object ? lot.client.id : undefined,
    unknown_client: typeof lot.client === 'string' ? lot.client : undefined,
    carbure_delivery_site_depot_id: lot.delivery_site instanceof Object ? lot.delivery_site.depot_id : undefined,
    unknown_delivery_site: typeof lot.delivery_site === 'string' ? lot.delivery_site : undefined,
    delivery_site_country_code: lot.delivery_site_country?.code_pays
  }
}

