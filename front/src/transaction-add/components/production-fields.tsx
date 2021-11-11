import { useTranslation } from "react-i18next"
import Autocomplete from "common-v2/components/autocomplete"
import { Fieldset, useBind, useFormContext } from "common-v2/components/form"
import { DateInput, TextInput } from "common-v2/components/input"
import * as api from "common-v2/api"
import * as norm from "common-v2/normalizers"
import { LotFormValue } from "./form"

export const ProductionFields = () => {
  const { t } = useTranslation()
  return (
    <Fieldset label={t("Production")}>
      <ProductionSiteField />
      <ProductionSiteCertificateField />
      <ProductionSiteDoubleCountingCertificateField />
      <ProductionCountryField />
      <ProductionSiteCommissioningDateField />
    </Fieldset>
  )
}

export const ProductionSiteField = () => {
  const { t } = useTranslation()
  const { value, bind } = useFormContext<LotFormValue>()
  const producer = norm.id(value.producer)
  return (
    <Autocomplete
      label={t("Site de production")}
      getOptions={(query) => api.findProductionSites(query, producer)}
      normalize={norm.normalizeProductionSite}
      {...bind("production_site")}
    />
  )
}

export const ProductionSiteCertificateField = () => {
  const { t } = useTranslation()
  const { value, bind } = useFormContext<LotFormValue>()
  const production_site = norm.id(value.production_site)
  return (
    <Autocomplete
      label={t("Certificat du site de production")}
      getOptions={(query) => api.findCertificates(query, { production_site })} // prettier-ignore
      {...bind("production_site_certificate")}
    />
  )
}

export const ProductionSiteDoubleCountingCertificateField = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  return (
    <TextInput
      label={t("Certificat double-comptage")}
      {...bind("production_site_double_counting_certificate")}
    />
  )
}

export const ProductionCountryField = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  return (
    <Autocomplete
      label={t("Pays de production")}
      getOptions={api.findCountries}
      normalize={norm.normalizeCountry}
      {...bind("production_country")}
    />
  )
}

export const ProductionSiteCommissioningDateField = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  return (
    <DateInput
      label={t("Date de mise en service")}
      {...bind("production_site_commissioning_date")}
    />
  )
}

export default ProductionFields
