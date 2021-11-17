import { useTranslation } from "react-i18next"
import { Fieldset, useBind, useFormContext } from "common-v2/components/form"
import Autocomplete from "common-v2/components/autocomplete"
import { DateInput } from "common-v2/components/input"
import { UserCheck } from "common-v2/components/icons"
import * as api from "common-v2/api"
import * as norm from "common-v2/utils/normalizers"
import { LotFormValue } from "./form"

export const DeliveryFields = () => {
  const { t } = useTranslation()
  return (
    <Fieldset label={t("Livraison")}>
      <SupplierField />
      <SupplierCertificateField />
      <ClientField />
      <DeliverySiteField />
      <DeliverySiteCountryField />
      <DeliveryDateField />
    </Fieldset>
  )
}

export const SupplierField = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  const props = bind("supplier")
  const isKnown = props.value instanceof Object

  return (
    <Autocomplete
      label={t("Fournisseur")}
      icon={isKnown ? UserCheck : undefined}
      create={norm.identity}
      defaultOptions={props.value ? [props.value] : undefined}
      getOptions={api.findEntities}
      normalize={norm.normalizeEntity}
      {...props}
    />
  )
}

export const SupplierCertificateField = () => {
  const { t } = useTranslation()
  const { value, bind } = useFormContext<LotFormValue>()
  const props = bind("supplier_certificate")

  // prettier-ignore
  const entity_id =
    value.supplier instanceof Object
      ? value.supplier.id
      : undefined

  return (
    <Autocomplete
      label={t("Certificat du fournisseur")}
      defaultOptions={props.value ? [props.value] : undefined}
      getOptions={(query) => api.findCertificates(query, { entity_id })}
      {...props}
    />
  )
}

export const ClientField = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  const props = bind("client")
  const isKnown = props.value instanceof Object

  return (
    <Autocomplete
      label={t("Client")}
      icon={isKnown ? UserCheck : undefined}
      create={norm.identity}
      defaultOptions={props.value ? [props.value] : undefined}
      getOptions={api.findEntities}
      normalize={norm.normalizeEntity}
      {...props}
    />
  )
}

export const DeliverySiteField = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  const props = bind("delivery_site")
  const isKnown = props.value instanceof Object

  return (
    <Autocomplete
      label={t("Site de livraison")}
      icon={isKnown ? UserCheck : undefined}
      create={norm.identity}
      defaultOptions={props.value ? [props.value] : undefined}
      getOptions={api.findDepots}
      normalize={norm.normalizeDepot}
      {...props}
    />
  )
}

export const DeliverySiteCountryField = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  const props = bind("delivery_site_country")

  return (
    <Autocomplete
      label={t("Pays de livraison")}
      defaultOptions={props.value ? [props.value] : undefined}
      getOptions={api.findCountries}
      normalize={norm.normalizeCountry}
      {...props}
    />
  )
}

export const DeliveryDateField = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  return (
    <DateInput
      required
      label={t("Date de livraison")}
      {...bind("delivery_date")}
    />
  )
}

export default DeliveryFields
