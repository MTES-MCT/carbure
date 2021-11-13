import { Lot } from "transactions-v2/types"
import Form, { useForm } from "common-v2/components/form"
import LotFields from "./lot-fields"
import ProductionFields from "./production-fields"
import DeliveryFields from "./delivery-fields"
import { EmissionFields, ReductionFields } from "./ghg-fields"

export interface LotFormProps {
  value?: LotFormValue
  onSubmit?: (value?: LotFormValue) => void
}

export const LotForm = ({ value, onSubmit }: LotFormProps) => {
  const form = useLotForm(value)

  return (
    <Form id="lot-form" variant="complex" form={form} onSubmit={onSubmit}>
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
  biofuel: "ETH" as string | undefined,
  feedstock: "COLZA" as string | undefined,
  country_of_origin: undefined as string | undefined,

  producer: undefined as number | string | undefined,
  supplier: undefined as number | string | undefined,
  supplier_certificate: undefined as string | undefined,
  free_field: undefined as string | undefined,

  production_site: undefined as number | string | undefined,
  production_site_certificate: undefined as string | undefined,
  production_country: undefined as string | undefined,
  production_site_double_counting_certificate: undefined as string | undefined,
  production_site_commissioning_date: undefined as string | undefined,

  client: undefined as number | string | undefined,
  delivery_site: undefined as string | undefined,
  delivery_site_country: undefined as string | undefined,
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

export default LotForm
