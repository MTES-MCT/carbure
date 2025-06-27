import React from "react"
import { useTranslation } from "react-i18next"
import useEntity from "common/hooks/entity"
import Autocomplete, { AutocompleteProps } from "common/components/autocomplete"
import { Fieldset, useFormContext } from "common/components/form"
import {
  DateInput,
  DateInputProps,
  TextInput,
  TextInputProps,
} from "common/components/input"
import * as api from "common/api"
import * as norm from "common/utils/normalizers"
import { LotFormValue } from "./lot-form"
import { UserCheck } from "common/components/icons"
import { Country, ProductionSite, EntityPreview } from "common/types"
import CertificateIcon from "transaction-details/components/lots/certificate"
import { isSAF } from "saf/utils/guards"

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

export const ProducerField = (
  props: AutocompleteProps<EntityPreview | string>
) => {
  const { t } = useTranslation()
  const { value, bind, setField } = useFormContext<LotFormValue>()
  const producer = value.producer
  const isKnown = producer instanceof Object

  // Function to create unknown producer when user types free text
  const createUnknownProducer = (text: string): string => {
    return text
  }

  const handleChange = (newValue: EntityPreview | string | undefined) => {
    setField("producer", newValue)
  }

  // If producer is a string (unknown producer), add it to defaultOptions
  // so the Autocomplete can display it correctly
  const defaultOptions = React.useMemo(() => {
    if (typeof producer === "string" && producer) {
      return [producer]
    }
    return producer && typeof producer === "object" ? [producer] : undefined
  }, [producer])

  return (
    <Autocomplete
      label={t("Producteur")}
      value={producer}
      defaultOptions={defaultOptions}
      icon={isKnown ? UserCheck : undefined}
      getOptions={api.findProducers}
      normalize={norm.normalizeEntityPreviewOrUnknown}
      create={createUnknownProducer}
      onChange={handleChange}
      error={bind("producer").error}
      {...props}
    />
  )
}

export const ProductionSiteField = (
  props: AutocompleteProps<ProductionSite | string>
) => {
  const { t } = useTranslation()
  const { value, bind, setField, setDisabledFields } =
    useFormContext<LotFormValue>()

  const { value: productionSite, ...bound } = bind("production_site")
  const isKnown = productionSite instanceof Object

  const producer = value.producer instanceof Object ? value.producer.id : undefined // prettier-ignore

  const handleChange = (newSite: ProductionSite | string | undefined) => {
    setField("production_site", newSite)

    if (!newSite) {
      setField("production_country", undefined)
      setField("production_site_commissioning_date", undefined)
      setField("production_site_double_counting_certificate", undefined)
      setDisabledFields([])
    } else if (
      typeof newSite === "object" &&
      "dc_reference" in newSite &&
      newSite.dc_reference
    ) {
      setField(
        "production_site_double_counting_certificate",
        newSite.dc_reference
      )
    }
  }

  // for unknown producers, we show a simple input to type unknown production sites
  if (producer === undefined) {
    return (
      <TextInput
        label={t("Site de production")}
        icon={isKnown ? UserCheck : undefined}
        value={isKnown ? productionSite.name : productionSite}
        onChange={(newValue) => handleChange(newValue)}
        error={bound.error}
        {...(props as TextInputProps)}
      />
    )
  }

  // otherwise autocomplete the producer's production sites
  return (
    <Autocomplete
      required
      label={t("Site de production")}
      value={productionSite}
      icon={isKnown ? UserCheck : undefined}
      defaultOptions={isKnown ? [productionSite] : undefined}
      getOptions={(query) => api.findProductionSites(query, producer)}
      normalize={norm.normalizeProductionSiteOrUnknown}
      onChange={handleChange}
      error={bound.error}
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

  const certificate =
    value.certificates?.production_site_certificate ?? undefined

  // if the production site is known, only propose its own certificates
  return (
    <Autocomplete
      icon={<CertificateIcon certificate={certificate} />}
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
  props: AutocompleteProps<string>
) => {
  const { t } = useTranslation()
  const { value, bind, setField, setDisabledFields } =
    useFormContext<LotFormValue>()
  const entity = useEntity()
  const lastResultsRef = React.useRef<any[]>([])
  const isAdminEditing = value.lot === undefined && entity.isAdmin

  // hide field for non-DC feedstocks
  if (!value.feedstock?.is_double_compte && !isAdminEditing) {
    return null
  }

  const bound = bind("production_site_double_counting_certificate")
  const isKnown =
    value.production_site && typeof value.production_site === "object"

  const certificate =
    value.certificates?.production_site_double_counting_certificate ?? undefined

  if (isKnown) {
    return (
      <TextInput
        disabled
        icon={<CertificateIcon certificate={certificate} />}
        label={t("Certificat double-comptage")}
        value={value.production_site_double_counting_certificate || ""}
        error={bound.error}
        {...props}
      />
    )
  }

  const getOptionsWithStore = async (query: string) => {
    const results = await api.findDcAgreements(query)
    lastResultsRef.current = results
    return results.map((item: any) => item.certificate_id)
  }

  const handleChange = (selectedId: string | undefined) => {
    setField("production_site_double_counting_certificate", selectedId)

    if (!selectedId) {
      setDisabledFields([])
      return
    }

    const selected = lastResultsRef.current.find(
      (item) => item.certificate_id === selectedId
    )
    if (selected) {
      setField("production_country", selected.production_site.country)
      setField("producer", selected.producer)
      setField("production_site", selected.production_site)
      setField(
        "production_site_commissioning_date",
        selected.production_site.date_mise_en_service
      )
      setDisabledFields([
        "production_country",
        "production_site_commissioning_date",
      ])
    }
  }

  return (
    <Autocomplete
      icon={<CertificateIcon certificate={certificate} />}
      label={t("Certificat double-comptage")}
      required={!isSAF(value.biofuel)}
      getOptions={getOptionsWithStore}
      normalize={(id: string) => ({ label: id, value: id })}
      value={value.production_site_double_counting_certificate || ""}
      error={bound.error}
      onChange={handleChange}
      {...props}
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
      ? {
          ...props,
          disabled: true,
          error: bound.error,
          value: value.production_site.date_mise_en_service ?? "",
        }
      : { ...props, ...bound, required: true }

  return <DateInput label={t("Date de mise en service")} {...dateProps} />
}

export default ProductionFields
