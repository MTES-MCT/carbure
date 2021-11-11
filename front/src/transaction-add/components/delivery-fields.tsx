import { useTranslation } from "react-i18next"
import Autocomplete from "common-v2/components/autocomplete"
import { Fieldset, useBind } from "common-v2/components/form"
import { DateInput } from "common-v2/components/input"
import * as api from "common-v2/api"
import * as norm from "common-v2/normalizers"
import { LotFormValue } from "./form"

export const DeliveryFields = () => {
  const { t } = useTranslation()
  return (
    <Fieldset label={t("Livraison")}>
      <ClientField />
      <DeliverySiteField />
      <DeliverySiteCountryField />
      <DeliveryDateField />
    </Fieldset>
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
