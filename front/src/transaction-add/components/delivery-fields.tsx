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
  const { value, bind } = useFormContext<LotFormValue>()
  const isKnown = value.lot && value.lot.carbure_supplier !== null
  return (
    <Autocomplete
      label={t("Fournisseur")}
      getOptions={api.findEntities}
      normalize={norm.normalizeEntity}
      icon={isKnown ? UserCheck : undefined}
      {...bind("supplier")}
    />
  )
}

export const SupplierCertificateField = () => {
  const { t } = useTranslation()
  const { value, bind } = useFormContext<LotFormValue>()
  const entity_id = parseInt(String(value.supplier))
  return (
    <Autocomplete
      label={t("Certificat du fournisseur")}
      getOptions={(query) => api.findCertificates(query, { entity_id })}
      {...bind("supplier_certificate")}
    />
  )
}

export const ClientField = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  return (
    <Autocomplete
      label={t("Client")}
      getOptions={api.findEntities}
      normalize={norm.normalizeEntity}
      {...bind("client")}
    />
  )
}

export const DeliverySiteField = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  return (
    <Autocomplete
      label={t("Site de livraison")}
      getOptions={api.findDepots}
      normalize={norm.normalizeDepot}
      {...bind("delivery_site")}
    />
  )
}

export const DeliverySiteCountryField = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  return (
    <Autocomplete
      label={t("Pays de livraison")}
      getOptions={api.findCountries}
      normalize={norm.normalizeCountry}
      {...bind("delivery_site_country")}
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
