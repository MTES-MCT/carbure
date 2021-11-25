export interface LotPayload {
  transport_document_type: string | undefined
  transport_document_reference: string | undefined
  volume: number | undefined
  biofuel_code: string | undefined
  feedstock_code: string | undefined
  country_code: string | undefined
  free_field: string | undefined

  eec: number | undefined
  el: number | undefined
  ep: number | undefined
  etd: number | undefined
  eu: number | undefined
  esca: number | undefined
  eccs: number | undefined
  eccr: number | undefined
  eee: number | undefined

  // production
  carbure_producer_id: number | undefined // ignored by backend
  unknown_producer: string | undefined
  carbure_production_site_id: number | undefined
  unknown_production_site: string | undefined
  production_site_certificate: string | undefined
  production_site_certificate_type: string | undefined
  production_country_code: string | undefined
  production_site_commissioning_date: string | undefined
  production_site_double_counting_certificate: string | undefined

  // supplier
  carbure_supplier_id: number | undefined // ignored by backend
  unknown_supplier: string | undefined
  supplier_certificate: string | undefined
  supplier_certificate_type: string | undefined

  // delivery
  delivery_date: string | undefined
  carbure_client_id: number | undefined
  unknown_client: string | undefined
  unknown_delivery_site: string | undefined
  carbure_delivery_site_depot_id: string | undefined
  delivery_site_country_code: string | undefined
}