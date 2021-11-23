import { useTranslation } from "react-i18next"
import Autocomplete, {
  AutocompleteProps,
} from "common-v2/components/autocomplete"
import { Fieldset, useBind, useFormContext } from "common-v2/components/form"
import {
  DateInput,
  DateInputProps,
  TextInput,
  TextInputProps,
} from "common-v2/components/input"
import * as api from "common-v2/api"
import * as norm from "common-v2/utils/normalizers"
import { LotFormValue } from "./lot-form"
import { UserCheck } from "common-v2/components/icons"
import { Entity } from "carbure/types"
import { Country, ProductionSite } from "common/types"

interface ProductionFieldsProps {
  readOnly?: boolean
}

export const ProductionFields = (props: ProductionFieldsProps) => {
  const { t } = useTranslation()
  return (
    <Fieldset label={t("Production")}>
      <ProducerField {...props} />
      <ProductionSiteField {...props} />
      <ProductionSiteCertificateField {...props} />
      <ProductionSiteDoubleCountingCertificateField {...props} />
      <ProductionCountryField {...props} />
      <ProductionSiteCommissioningDateField {...props} />
    </Fieldset>
  )
}

export const ProducerField = (props: AutocompleteProps<Entity | string>) => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  const bound = bind("producer")
  const isKnown = bound.value instanceof Object

  return (
    <Autocomplete
      label={t("Producteur")}
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

export const ProductionSiteField = (
  props: AutocompleteProps<ProductionSite | string>
) => {
  const { t } = useTranslation()
  const { value, bind } = useFormContext<LotFormValue>()
  const bound = bind("production_site")

  const isKnown = bound.value instanceof Object

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
      defaultOptions={bound.value ? [bound.value] : undefined}
      getOptions={(query) => api.findProductionSites(query, producer)}
      normalize={norm.normalizeProductionSite}
      {...bound}
      {...props}
    />
  )
}

export const ProductionSiteCertificateField = (
  props: AutocompleteProps<string>
) => {
  const { t } = useTranslation()
  const { value, bind } = useFormContext<LotFormValue>()
  const bound = bind("production_site_certificate")

  const production_site =
    value.production_site instanceof Object
      ? value.production_site.id
      : undefined

  return (
    <Autocomplete
      label={t("Certificat du site de production")}
      defaultOptions={bound.value ? [bound.value] : undefined}
      getOptions={(query) => api.findCertificates(query, { production_site })} // prettier-ignore
      {...bound}
      {...props}
    />
  )
}

export const ProductionSiteDoubleCountingCertificateField = (
  props: TextInputProps
) => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  return (
    <TextInput
      label={t("Certificat double-comptage")}
      {...bind("production_site_double_counting_certificate")}
      {...props}
    />
  )
}

export const ProductionCountryField = (props: AutocompleteProps<Country>) => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  const bound = bind("production_country")
  return (
    <Autocomplete
      label={t("Pays de production")}
      defaultOptions={bound.value ? [bound.value] : undefined}
      getOptions={api.findCountries}
      normalize={norm.normalizeCountry}
      {...bound}
      {...props}
    />
  )
}

export const ProductionSiteCommissioningDateField = (props: DateInputProps) => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  return (
    <DateInput
      label={t("Date de mise en service")}
      {...bind("production_site_commissioning_date")}
      {...props}
    />
  )
}

export default ProductionFields
