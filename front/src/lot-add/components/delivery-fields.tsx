import { useTranslation } from "react-i18next"
import useEntity from "carbure/hooks/entity"
import { Fieldset, useBind, useFormContext } from "common-v2/components/form"
import Autocomplete, {
  AutocompleteProps,
} from "common-v2/components/autocomplete"
import { DateInput, DateInputProps } from "common-v2/components/input"
import { UserCheck } from "common-v2/components/icons"
import * as api from "common-v2/api"
import * as norm from "common-v2/utils/normalizers"
import { LotFormValue } from "./lot-form"
import { Entity } from "carbure/types"
import { Country, Depot } from "common/types"

interface DeliveryFieldsProps {
  readOnly?: boolean
}

export const DeliveryFields = (props: DeliveryFieldsProps) => {
  const { t } = useTranslation()
  return (
    <Fieldset label={t("Livraison")}>
      <SupplierField {...props} />
      <SupplierCertificateField {...props} />
      <ClientField {...props} />
      <DeliverySiteField {...props} />
      <DeliverySiteCountryField {...props} />
      <DeliveryDateField {...props} />
    </Fieldset>
  )
}

export const SupplierField = (props: AutocompleteProps<Entity | string>) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const bind = useBind<LotFormValue>()

  const { value: supplier, ...bound } = bind("supplier")
  const isKnown = supplier instanceof Object

  return (
    <Autocomplete
      label={t("Fournisseur")}
      value={supplier}
      icon={isKnown ? UserCheck : undefined}
      create={norm.identity}
      defaultOptions={isKnown ? [supplier] : [entity]}
      getOptions={async () => [entity]}
      normalize={norm.normalizeEntity}
      {...bound}
      {...props}
    />
  )
}

export const SupplierCertificateField = (props: AutocompleteProps<string>) => {
  const { t } = useTranslation()
  const { value, bind } = useFormContext<LotFormValue>()
  const bound = bind("supplier_certificate")

  const supplier = value.supplier instanceof Object ? value.supplier : undefined

  return (
    <Autocomplete
      label={t("Certificat du fournisseur")}
      placeholder={supplier?.default_certificate}
      defaultOptions={bound.value ? [bound.value] : undefined}
      getOptions={(query) =>
        api.findCertificates(query, { entity_id: supplier?.id })
      }
      {...bound}
      {...props}
    />
  )
}

export const ClientField = (props: AutocompleteProps<Entity | string>) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const bind = useBind<LotFormValue>()
  const bound = bind("client")
  const isKnown = bound.value instanceof Object

  return (
    <Autocomplete
      disabled={entity.isOperator && !entity.has_mac}
      label={t("Client")}
      placeholder={entity.isOperator ? entity.name : undefined}
      icon={isKnown ? UserCheck : undefined}
      create={norm.identity}
      defaultOptions={bound.value ? [bound.value] : undefined}
      getOptions={api.findEntities}
      normalize={norm.normalizeEntity}
      {...bound}
      {...props}
    />
  )
}

export const DeliverySiteField = (props: AutocompleteProps<Depot | string>) => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  const bound = bind("delivery_site")
  const isKnown = bound.value instanceof Object

  return (
    <Autocomplete
      label={t("Site de livraison")}
      icon={isKnown ? UserCheck : undefined}
      create={norm.identity}
      defaultOptions={bound.value ? [bound.value] : undefined}
      getOptions={api.findDepots}
      normalize={norm.normalizeDepot}
      {...bound}
      {...props}
    />
  )
}

export const DeliverySiteCountryField = (props: AutocompleteProps<Country>) => {
  const { t } = useTranslation()
  const { value, bind } = useFormContext<LotFormValue>()
  const bound = bind("delivery_site_country")

  return (
    <Autocomplete
      disabled={value.delivery_site instanceof Object}
      label={t("Pays de livraison")}
      defaultOptions={bound.value ? [bound.value] : undefined}
      getOptions={api.findCountries}
      normalize={norm.normalizeCountry}
      {...bound}
      {...props}
    />
  )
}

export const DeliveryDateField = (props: DateInputProps) => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  return (
    <DateInput
      required
      label={t("Date de livraison")}
      {...bind("delivery_date")}
      {...props}
    />
  )
}

export default DeliveryFields
