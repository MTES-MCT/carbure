import { useTranslation } from "react-i18next"
import { Fieldset, useBind, useFormContext } from "common/components/form"
import Autocomplete, { AutocompleteProps } from "common/components/autocomplete"
import { DateInput, DateInputProps, TextInput } from "common/components/input"
import { UserCheck } from "common/components/icons"
import * as api from "common/api"
import * as norm from "common/utils/normalizers"
import { compact, uniqueBy } from "common/utils/collection"
import { Country, EntityPreview, Site, SiteType } from "common/types"
import CertificateIcon from "transaction-details/components/lots/certificate"
import {
  LotFormValue,
  isLotClient,
  isLotProducer,
  isLotSupplier,
  isLotVendor,
} from "./lot-form"
import useEntity from "common/hooks/entity"

interface DispatchFieldsProps {
  readOnly?: boolean
}

const DISPATCH_SITE_TYPES: SiteType[] = [
  SiteType.EFS,
  SiteType.EFPE,
  SiteType.OIL_DEPOT,
  SiteType.BIOFUEL_DEPOT,
  SiteType.PRODUCTION_BIOLIQUID,
  SiteType.EFCA,
]

export const DispatchFields = (props: DispatchFieldsProps) => {
  const { t } = useTranslation()

  return (
    <Fieldset label={t("Expédition")}>
      <SupplierField {...props} />
      <SupplierCertificateField {...props} />
      <MyCertificateField {...props} />
      <DispatchSiteField {...props} />
      <DispatchSiteCountryField {...props} />
      <DispatchDateField {...props} />
    </Fieldset>
  )
}

export const SupplierField = (
  props: AutocompleteProps<EntityPreview | string>
) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { value, bind } = useFormContext<LotFormValue>()

  const { value: supplier, ...bound } = bind("supplier")
  const isKnown = supplier instanceof Object

  const defaultOptions = uniqueBy(
    compact([supplier, entity]),
    (v) => norm.normalizeEntityPreviewOrUnknown(v).label
  )

  if (entity.isAdmin) {
    return (
      <Autocomplete
        label={t("Fournisseur")}
        value={supplier}
        icon={isKnown ? UserCheck : undefined}
        create={norm.identity}
        defaultOptions={supplier ? [supplier] : undefined}
        getOptions={api.findBiofuelEntities}
        normalize={norm.normalizeEntityPreviewOrUnknown}
        {...bound}
        {...props}
      />
    )
  }

  return (
    <Autocomplete
      label={t("Fournisseur")}
      value={supplier}
      icon={isKnown ? UserCheck : undefined}
      create={norm.identity}
      defaultOptions={defaultOptions}
      getOptions={async () => [entity]}
      normalize={norm.normalizeEntityPreviewOrUnknown}
      {...bound}
      {...props}
      disabled={
        props.disabled || bound.disabled || isLotProducer(entity, value)
      }
    />
  )
}

export const SupplierCertificateField = (props: AutocompleteProps<string>) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { value, bind } = useFormContext<LotFormValue>()

  const date = value.delivery_date
  const certificate = value.certificates?.supplier_certificate ?? undefined
  const bound = bind("supplier_certificate")

  return (
    <Autocomplete
      required={isLotClient(entity, value)}
      label={t("Certificat du fournisseur")}
      icon={<CertificateIcon certificate={certificate} />}
      defaultOptions={bound.value ? [bound.value] : undefined}
      getOptions={(query) =>
        isLotSupplier(entity, value)
          ? api.findMyCertificates(query, { entity_id: entity.id, date })
          : api.findCertificates(query, { date })
      }
      {...bound}
      {...props}
    />
  )
}

export const MyCertificateField = (props: AutocompleteProps<string>) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { value, bind } = useFormContext<LotFormValue>()
  const bound = bind("vendor_certificate")

  if (!isLotVendor(entity, value) || !entity.canTrade) {
    return null
  }

  const certificate = value.certificates?.vendor_certificate ?? undefined

  return (
    <Autocomplete
      required
      label={t("Votre certificat de négoce")}
      icon={<CertificateIcon certificate={certificate} />}
      defaultOptions={bound.value ? [bound.value] : undefined}
      getOptions={(query) =>
        api.findMyCertificates(query, { entity_id: entity.id })
      }
      {...bound}
      {...props}
    />
  )
}

export const DispatchSiteField = (props: AutocompleteProps<Site | string>) => {
  const { t } = useTranslation()
  const { bind } = useFormContext<LotFormValue>()
  const bound = bind("dispatch_site")
  const isKnown = bound.value instanceof Object

  return (
    <Autocomplete
      label={t("Site d'expédition")}
      icon={isKnown ? UserCheck : undefined}
      create={norm.identity}
      defaultOptions={bound.value ? [bound.value] : undefined}
      getOptions={(query) => api.findSites(query, DISPATCH_SITE_TYPES)}
      normalize={norm.normalizeSiteOrUnknown}
      {...bound}
      {...props}
    />
  )
}

export const DispatchSiteCountryField = (props: AutocompleteProps<Country>) => {
  const { t } = useTranslation()
  const { value, bind } = useFormContext<LotFormValue>()
  const bound = bind("dispatch_site_country")

  if (value.dispatch_site instanceof Object && value.dispatch_site.country) {
    return (
      <TextInput
        disabled
        readOnly={props.readOnly}
        label={t("Pays d'expédition")}
        value={norm.normalizeCountry(value.dispatch_site.country).label}
        error={bound.error}
      />
    )
  }

  return (
    <Autocomplete
      label={t("Pays d'expédition")}
      defaultOptions={bound.value ? [bound.value] : undefined}
      getOptions={api.findCountries}
      normalize={norm.normalizeCountry}
      {...bound}
      {...props}
    />
  )
}

export const DispatchDateField = (props: DateInputProps) => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()

  return (
    <DateInput
      label={t("Date d'expédition")}
      {...bind("dispatch_date")}
      {...props}
    />
  )
}

export default DispatchFields
