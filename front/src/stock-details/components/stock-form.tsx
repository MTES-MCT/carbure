import { Stock } from "transactions-v2/types"
import Form, { useForm } from "common-v2/components/form"
import { useEffect, useMemo } from "react"
import { Entity } from "carbure/types"
import {
  Biofuel,
  Country,
  Depot,
  Feedstock,
  ProductionSite,
} from "common/types"

export interface StockFormProps {
  stock?: Stock
  onSubmit?: (value?: StockFormValue) => void
}

export const StockForm = ({ stock, onSubmit }: StockFormProps) => {
  const value = useMemo(() => stockToFormValue(stock), [stock])
  const form = useStockForm(value)

  const setValue = form.setValue
  useEffect(() => {
    setValue(value)
  }, [value, setValue])

  return (
    <Form id="stock-form" variant="columns" form={form} onSubmit={onSubmit}>
      <h1>TODO</h1>
    </Form>
  )
}

export function useStockForm(initialValue: StockFormValue = defaultStock) {
  return useForm(initialValue)
}

export const defaultStock = {
  // save the whole stock data so we can access it in the form fields
  stock: undefined as Stock | undefined,

  biofuel: undefined as Biofuel | undefined,
  feedstock: undefined as Feedstock | undefined,
  country_of_origin: undefined as Country | undefined,

  production_site: undefined as ProductionSite | string | undefined,
  production_country: undefined as Country | undefined,

  supplier: undefined as Entity | string | undefined,
  client: undefined as Entity | string | undefined,
  depot: undefined as Depot | string | undefined,
  delivery_date: undefined as string | undefined,

  ghg_reduction: 0 as number | undefined,
  ghg_reduction_red_ii: 0 as number | undefined,
}

export type StockFormValue = typeof defaultStock

export const stockToFormValue: (stock: Stock | undefined) => StockFormValue = (
  stock
) => ({
  stock,

  volumne: stock?.initial_volume,
  remaining_volume: stock?.remaining_volume,
  biofuel: stock?.biofuel ?? undefined,
  feedstock: stock?.feedstock ?? undefined,
  country_of_origin: stock?.country_of_origin ?? undefined,
  production_site: stock?.carbure_production_site ?? stock?.unknown_production_site ?? undefined, // prettier-ignore
  production_country: stock?.production_country ?? undefined,
  supplier: stock?.carbure_supplier ?? stock?.unknown_supplier ?? undefined,
  client: stock?.carbure_client ?? undefined,
  depot: stock?.depot ?? undefined,
  delivery_date: stock?.delivery_date ?? undefined,
  ghg_reduction: stock?.ghg_reduction ?? undefined,
  ghg_reduction_red_ii: stock?.ghg_reduction_red_ii ?? undefined,
})

export default StockForm
