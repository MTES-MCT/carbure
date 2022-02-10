import { useTranslation } from "react-i18next"
import useEntity from "carbure/hooks/entity"
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
import CertificateIcon from "lot-details/components/certificate"

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
  const entity = useEntity()
  const bind = useBind<LotFormValue>()

  const { value, ...bound } = bind("producer")
  const isKnown = value instanceof Object

  if (!entity.isProducer) {
    return (
      <TextInput
        label={t("Producteur")}
        icon={isKnown ? UserCheck : undefined}
        value={isKnown ? value.name : value}
        {...bound}
        {...(props as TextInputProps)}
      />
    )
  }

  return (
    <Autocomplete
      disabled={!entity.has_trading && !entity.has_stocks}
      label={t("Producteur")}
      value={value}
      icon={isKnown ? UserCheck : undefined}
      create={norm.identity}
      defaultOptions={value ? [value] : [entity]}
      normalize={norm.normalizeEntityOrUnknown}
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

  const { value: productionSite, ...bound } = bind("production_site")
  const isKnown = productionSite instanceof Object

  const isKnownProducer = value.producer instanceof Object
  const producer =
    value.producer instanceof Object ? value.producer.id : undefined

  if (!isKnownProducer) {
    return (
      <TextInput
        label={t("Site de production")}
        icon={isKnown ? UserCheck : undefined}
        value={isKnown ? productionSite.name : productionSite}
        {...bound}
        {...(props as TextInputProps)}
      />
    )
  }

  return (
    <Autocomplete
      label={t("Site de production")}
      value={productionSite}
      icon={isKnown ? UserCheck : undefined}
      create={norm.identity}
      defaultOptions={isKnown ? [productionSite] : undefined}
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
  const entity = useEntity()
  const { value, bind } = useFormContext<LotFormValue>()
  const bound = bind("production_site_certificate")

  const production_site_id =
    value.production_site instanceof Object
      ? value.production_site.id
      : undefined

  // prettier-ignore
  const icon = value.certificates?.production_site_certificate
    ? <CertificateIcon certificate={value.certificates?.production_site_certificate} />
    : undefined

  return (
    <Autocomplete
      icon={icon}
      label={t("Certificat du site de production")}
      defaultOptions={bound.value ? [bound.value] : undefined}
      getOptions={(query) =>
        production_site_id !== undefined
          ? api.findMyCertificates(query, {
              entity_id: entity.id,
              production_site_id,
            })
          : api.findCertificates(query)
      }
      {...bound}
      {...props}
    />
  )
}

export const ProductionSiteDoubleCountingCertificateField = (
  props: TextInputProps
) => {
  const { t } = useTranslation()
  const { value, bind } = useFormContext<LotFormValue>()
  const bound = bind("production_site_double_counting_certificate")

  const dcProps =
    value.production_site instanceof Object
      ? { ...props, disabled: true, error: bound.error, value: value.production_site.dc_reference } // prettier-ignore
      : { ...props, ...bound }

  // prettier-ignore
  const icon = value.certificates?.production_site_double_counting_certificate
    ? <CertificateIcon certificate={value.certificates?.production_site_double_counting_certificate} />
    : undefined

  return (
    <TextInput
      icon={icon}
      label={t("Certificat double-comptage")}
      {...dcProps}
    />
  )
}

export const ProductionCountryField = (props: AutocompleteProps<Country>) => {
  const { t } = useTranslation()
  const { value, bind } = useFormContext<LotFormValue>()
  const bound = bind("production_country")

  if (value.production_site instanceof Object) {
    return (
      <TextInput
        disabled
        readOnly={props.readOnly}
        label={t("Pays de production")}
        value={norm.normalizeCountry(value.production_site.country).label}
        error={bound.error}
      />
    )
  }

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
  const { value, bind } = useFormContext<LotFormValue>()
  const bound = bind("production_site_commissioning_date")

  const dateProps =
    value.production_site instanceof Object
      ? { ...props, disabled: true, error: bound.error, value: value.production_site.date_mise_en_service } // prettier-ignore
      : { ...props, ...bound }

  return <DateInput label={t("Date de mise en service")} {...dateProps} />
}

export default ProductionFields
