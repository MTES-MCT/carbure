import { Lot } from "transactions-v2/types"
import Form, { useForm } from "common-v2/components/form"
import LotFields from "./lot-fields"
import ProductionFields from "./production-fields"
import DeliveryFields from "./delivery-fields"
import { EmissionFields, ReductionFields } from "./ghg-fields"
import { useEffect, useMemo } from "react"
import { Entity } from "carbure/types"
import { Biofuel, Country, Depot, Feedstock, ProductionSite } from "common/types"

export interface LotFormProps {
  lot?: Lot
  onSubmit?: (value?: LotFormValue) => void
}

export const LotForm = ({ lot, onSubmit }: LotFormProps) => {
  const value = useMemo(() => lotToFormValue(lot), [lot])
  const form = useLotForm(value)

  const setValue = form.setValue
  useEffect(() => {
    setValue(value)
  }, [value, setValue])

  return (
    <Form id="lot-form" variant="columns" form={form} onSubmit={onSubmit}>
      <LotFields />
      <ProductionFields />
      <DeliveryFields />
      <EmissionFields />
      <ReductionFields />
    </Form>
  )
}

export function useLotForm(initialValue: LotFormValue = defaultLot) {
  return useForm(initialValue)
}

export const defaultLot = {
  // save the whole Lot data so we can access it in the form fields
  lot: undefined as Lot | undefined,

  transport_document_reference: undefined as string | undefined,
  volume: 0 as number | undefined,
  biofuel: undefined as Biofuel | undefined,
  feedstock: undefined as Feedstock | undefined,
  country_of_origin: undefined as Country | undefined,
  free_field: undefined as string | undefined,

  producer: undefined as Entity | string | undefined,
  production_site: undefined as ProductionSite | string | undefined,
  production_site_certificate: undefined as string | undefined,
  production_country: undefined as Country | undefined,
  production_site_double_counting_certificate: undefined as string | undefined,
  production_site_commissioning_date: undefined as string | undefined,

  supplier: undefined as Entity | string | undefined,
  supplier_certificate: undefined as string | undefined,
  client: undefined as Entity | string | undefined,
  delivery_site: undefined as Depot | string | undefined,
  delivery_site_country: undefined as Country | undefined,
  delivery_date: undefined as string | undefined,

  eec: 0 as number | undefined,
  el: 0 as number | undefined,
  ep: 0 as number | undefined,
  etd: 0 as number | undefined,
  eu: 0 as number | undefined,

  esca: 0 as number | undefined,
  eccs: 0 as number | undefined,
  eccr: 0 as number | undefined,
  eee: 0 as number | undefined,

  ghg_total: 0 as number | undefined,
  ghg_reduction: 0 as number | undefined,
  ghg_reduction_red_ii: 0 as number | undefined,
}

export type LotFormValue = typeof defaultLot

export const lotToFormValue: (lot: Lot | undefined) => LotFormValue = (lot) => ({
  lot,

  transport_document_reference: lot?.transport_document_reference ?? undefined,
  volume: lot?.volume ?? undefined,
  biofuel: lot?.biofuel ?? undefined,
  feedstock: lot?.feedstock ?? undefined,
  country_of_origin: lot?.country_of_origin ?? undefined,
  free_field: lot?.free_field ?? undefined,

  producer: lot?.carbure_producer ?? lot?.unknown_producer ?? undefined,
  production_site: lot?.carbure_production_site ?? lot?.unknown_production_site ?? undefined,
  production_country: lot?.production_country ?? undefined,
  production_site_certificate: lot?.production_site_certificate ?? undefined,
  production_site_commissioning_date: lot?.production_site_commissioning_date ?? undefined,
  production_site_double_counting_certificate: lot?.production_site_double_counting_certificate ?? undefined,

  supplier: lot?.carbure_supplier ?? lot?.unknown_supplier ?? undefined,
  supplier_certificate: lot?.supplier_certificate ?? undefined,
  client: lot?.carbure_client ?? lot?.unknown_client ?? undefined,
  delivery_site: lot?.carbure_delivery_site ?? lot?.unknown_delivery_site ?? undefined,
  delivery_site_country: lot?.delivery_site_country ?? undefined,
  delivery_date: lot?.delivery_date ?? undefined,

  eec: lot?.eec ?? undefined,
  el: lot?.el ?? undefined,
  ep: lot?.ep ?? undefined,
  etd: lot?.etd ?? undefined,
  eu: lot?.eu ?? undefined,

  esca: lot?.esca ?? undefined,
  eccs: lot?.eccs ?? undefined,
  eccr: lot?.eccr ?? undefined,
  eee: lot?.eee ?? undefined,

  ghg_total: lot?.ghg_total ?? undefined,
  ghg_reduction: lot?.ghg_reduction ?? undefined,
  ghg_reduction_red_ii: lot?.ghg_reduction_red_ii ?? undefined,
})

export default LotForm
