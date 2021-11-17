import { useTranslation } from "react-i18next"
import Autocomplete from "common-v2/components/autocomplete"
import { Fieldset, useBind, useFormContext } from "common-v2/components/form"
import { DateInput, TextInput } from "common-v2/components/input"
import * as api from "common-v2/api"
import * as norm from "common-v2/utils/normalizers"
import { LotFormValue } from "./lot-form"
import { UserCheck } from "common-v2/components/icons"

export const ProductionFields = () => {
  const { t } = useTranslation()
  return (
    <Fieldset label={t("Production")}>
      <ProducerField />
      <ProductionSiteField />
      <ProductionSiteCertificateField />
      <ProductionSiteDoubleCountingCertificateField />
      <ProductionCountryField />
      <ProductionSiteCommissioningDateField />
    </Fieldset>
  )
}

export const ProducerField = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  const props = bind("producer")
  const isKnown = props.value instanceof Object

  return (
    <Autocomplete
      label={t("Producteur")}
      icon={isKnown ? UserCheck : undefined}
      create={norm.identity}
      defaultOptions={props.value ? [props.value] : undefined}
      getOptions={api.findEntities}
      normalize={norm.normalizeEntity}
      {...props}
    />
  )
}

export const ProductionSiteField = () => {
  const { t } = useTranslation()
  const { value, bind } = useFormContext<LotFormValue>()
  const props = bind("production_site")

  const isKnown = props.value instanceof Object

  // prettier-ignore
  const producer =
    value.producer instanceof Object
      ? value.producer.id
      : undefined

  return (
    <Autocomplete
      label={t("Site de production")}
      icon={isKnown ? UserCheck : undefined}
      create={norm.identity}
      defaultOptions={props.value ? [props.value] : undefined}
      getOptions={(query) => api.findProductionSites(query, producer)}
      normalize={norm.normalizeProductionSite}
      {...props}
    />
  )
}

export const ProductionSiteCertificateField = () => {
  const { t } = useTranslation()
  const { value, bind } = useFormContext<LotFormValue>()
  const props = bind("production_site_certificate")

  const production_site =
    value.production_site instanceof Object
      ? value.production_site.id
      : undefined

  return (
    <Autocomplete
      label={t("Certificat du site de production")}
      defaultOptions={props.value ? [props.value] : undefined}
      getOptions={(query) => api.findCertificates(query, { production_site })} // prettier-ignore
      {...props}
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
  const props = bind("production_country")
  return (
    <Autocomplete
      label={t("Pays de production")}
      defaultOptions={props.value ? [props.value] : undefined}
      getOptions={api.findCountries}
      normalize={norm.normalizeCountry}
      {...props}
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
