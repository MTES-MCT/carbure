import { useTranslation } from "react-i18next"
import { Fieldset, useBind } from "common-v2/components/form"
import Autocomplete, {
  AutocompleteProps,
} from "common-v2/components/autocomplete"
import { DateInput, DateInputProps } from "common-v2/components/input"
import { UserCheck } from "common-v2/components/icons"
import * as norm from "common-v2/utils/normalizers"
import { StockFormValue } from "./stock-form"
import { Entity } from "carbure/types"
import { Country, Depot, ProductionSite } from "common/types"

interface RouteFieldsProps {
  readOnly?: boolean
}

export const RouteFields = (props: RouteFieldsProps) => {
  const { t } = useTranslation()
  return (
    <Fieldset label={t("Parcours")}>
      <ProductionSiteField />
      <ProductionCountryField />
      <SupplierField />
      <ClientField />
      <DepotField />
      <DeliveryDateField />
    </Fieldset>
  )
}

export const ProductionSiteField = (
  props: AutocompleteProps<ProductionSite | string>
) => {
  const { t } = useTranslation()
  const bind = useBind<StockFormValue>()
  const bound = bind("production_site")

  const isKnown = bound.value instanceof Object

  return (
    <Autocomplete
      readOnly
      label={t("Site de production")}
      icon={isKnown ? UserCheck : undefined}
      defaultOptions={bound.value ? [bound.value] : undefined}
      normalize={norm.normalizeProductionSite}
      {...bound}
      {...props}
    />
  )
}

export const ProductionCountryField = (props: AutocompleteProps<Country>) => {
  const { t } = useTranslation()
  const bind = useBind<StockFormValue>()
  const bound = bind("production_country")
  return (
    <Autocomplete
      readOnly
      label={t("Pays de production")}
      defaultOptions={bound.value ? [bound.value] : undefined}
      normalize={norm.normalizeCountry}
      {...bound}
      {...props}
    />
  )
}

export const SupplierField = (props: AutocompleteProps<Entity | string>) => {
  const { t } = useTranslation()
  const bind = useBind<StockFormValue>()
  const bound = bind("supplier")
  const isKnown = bound.value instanceof Object

  return (
    <Autocomplete
      readOnly
      label={t("Fournisseur")}
      icon={isKnown ? UserCheck : undefined}
      defaultOptions={bound.value ? [bound.value] : undefined}
      normalize={norm.normalizeEntity}
      {...bound}
      {...props}
    />
  )
}

export const ClientField = (props: AutocompleteProps<Entity | string>) => {
  const { t } = useTranslation()
  const bind = useBind<StockFormValue>()
  const bound = bind("client")
  const isKnown = bound.value instanceof Object

  return (
    <Autocomplete
      readOnly
      label={t("Client")}
      icon={isKnown ? UserCheck : undefined}
      defaultOptions={bound.value ? [bound.value] : undefined}
      normalize={norm.normalizeEntity}
      {...bound}
      {...props}
    />
  )
}

export const DepotField = (props: AutocompleteProps<Depot | string>) => {
  const { t } = useTranslation()
  const bind = useBind<StockFormValue>()
  const bound = bind("depot")
  const isKnown = bound.value instanceof Object

  return (
    <Autocomplete
      readOnly
      label={t("Site de livraison")}
      icon={isKnown ? UserCheck : undefined}
      defaultOptions={bound.value ? [bound.value] : undefined}
      normalize={norm.normalizeDepot}
      {...bound}
      {...props}
    />
  )
}

export const DeliveryDateField = (props: DateInputProps) => {
  const { t } = useTranslation()
  const bind = useBind<StockFormValue>()
  return (
    <DateInput
      readOnly
      label={t("Date de livraison")}
      {...bind("delivery_date")}
      {...props}
    />
  )
}

export default RouteFields
