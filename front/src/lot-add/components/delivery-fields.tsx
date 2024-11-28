import { useTranslation } from "react-i18next"
import useEntity, { EntityManager } from "carbure/hooks/entity"
import { Fieldset, useBind, useFormContext } from "common/components/form"
import Autocomplete, { AutocompleteProps } from "common/components/autocomplete"
import { DateInput, DateInputProps, TextInput } from "common/components/input"
import { UserCheck } from "common/components/icons"
import * as api from "carbure/api"
import * as norm from "carbure/utils/normalizers"
import {
  isExternalDelivery,
  isLotClient,
  isLotProducer,
  isLotSupplier,
  isLotVendor,
  LotFormValue,
} from "./lot-form"
import { LotStatus } from "transactions/types"
import { Country, Depot, EntityPreview } from "carbure/types"
import Select, { SelectProps } from "common/components/select"
import { DeliveryType } from "transactions/types"
import { compact, uniqueBy } from "common/utils/collection"
import CertificateIcon from "transaction-details/components/lots/certificate"

interface DeliveryFieldsProps {
  readOnly?: boolean
}

export const DeliveryFields = (props: DeliveryFieldsProps) => {
  const { t } = useTranslation()
  return (
    <Fieldset label={t("Livraison")}>
      <SupplierField {...props} />
      <SupplierCertificateField {...props} />
      <MyCertificateField {...props} />
      <ClientField {...props} />
      <DeliveryTypeField {...props} />
      <DeliverySiteField {...props} />
      <DeliverySiteCountryField {...props} />
      <DeliveryDateField {...props} />
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
          ? api.findMyCertificates(query, { entity_id: entity.id })
          : api.findCertificates(query)
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

  // hide this field if this entity is NOT an intermediary
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

export const ClientField = (
  props: AutocompleteProps<EntityPreview | string>
) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { value, bind } = useFormContext<LotFormValue>()
  const bound = bind("client")
  const isKnown = bound.value instanceof Object
  const hasClients = entity.has_mac || entity.has_direct_deliveries || entity.has_trading // prettier-ignore

  return (
    <Autocomplete
      required={!isExternalDelivery(value)}
      label={t("Client")}
      icon={isKnown ? UserCheck : undefined}
      create={norm.identity}
      defaultOptions={bound.value ? [bound.value] : undefined}
      getOptions={api.findBiofuelEntities}
      normalize={norm.normalizeEntityPreviewOrUnknown}
      {...bound}
      {...props}
      disabled={
        entity.isPowerOrHeatProducer ||
        (entity.isOperator && !hasClients) ||
        props.disabled ||
        bound.disabled
      }
    />
  )
}

// DeliveryType field should only appear when the client is either the current entity or an unknown one
export const DeliveryTypeField = (props: SelectProps<DeliveryType>) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { value, bind } = useFormContext<LotFormValue>()

  const deliveryTypes = getDeliveryTypes(
    entity,
    value.client,
    value.lot?.lot_status
  )

  if (deliveryTypes.length === 0 || value.lot?.lot_status === "PENDING") {
    return null
  }

  // prevent editing delivery type when doing a correction for a lot that duplicated for forwarding
  const isDraft = !value.lot || value.lot.lot_status === "DRAFT"

  const hasChildren =
    !!value.delivery_type &&
    [
      DeliveryType.Stock,
      DeliveryType.Processing,
      DeliveryType.Trading,
    ].includes(value.delivery_type)

  const bound = bind("delivery_type")

  return (
    <Select
      clear
      {...bound}
      label={t("Type de livraison")}
      placeholder={t("Choisissez un type")}
      normalize={norm.normalizeDeliveryType}
      options={deliveryTypes}
      {...props}
      disabled={
        entity.isPowerOrHeatProducer ||
        (!isDraft && hasChildren) ||
        props.disabled ||
        bound.disabled
      }
    />
  )
}

export function getDeliveryTypes(
  entity: EntityManager,
  client: EntityPreview | string | undefined,
  status: LotStatus = LotStatus.Draft
) {
  if (entity.isAdmin) {
    return [
      DeliveryType.Blending,
      DeliveryType.Exportation,
      DeliveryType.RFC,
      DeliveryType.Direct,
      DeliveryType.Stock,
      DeliveryType.Processing,
      DeliveryType.Trading,
    ]
  }

  const {
    isOperator,
    isPowerOrHeatProducer,
    has_stocks,
    has_mac,
    has_direct_deliveries,
    has_trading,
    isIndustry,
  } = entity
  const isClientEntity = client instanceof Object ? client.id === entity.id : false // prettier-ignore
  const isClientUnknown = client === undefined || typeof client === "string"

  return compact<DeliveryType>([
    isClientEntity && isOperator && DeliveryType.Blending,
    isClientEntity && has_stocks && DeliveryType.Stock,
    (isClientUnknown || isClientEntity) && has_mac && DeliveryType.RFC,
    (isClientUnknown || isClientEntity) && has_direct_deliveries && DeliveryType.Direct, // prettier-ignore
    isIndustry && (isClientUnknown || isClientEntity) && DeliveryType.Exportation, // prettier-ignore
    status !== LotStatus.Draft && has_trading && DeliveryType.Trading,
    isClientEntity && isPowerOrHeatProducer && DeliveryType.Consumption,
  ])
}

export const DeliverySiteField = (props: AutocompleteProps<Depot | string>) => {
  const { t } = useTranslation()
  const { value, bind } = useFormContext<LotFormValue>()
  const bound = bind("delivery_site")
  const isKnown = bound.value instanceof Object

  return (
    <Autocomplete
      required={!isExternalDelivery(value)}
      label={t("Site de livraison")}
      icon={isKnown ? UserCheck : undefined}
      create={norm.identity}
      defaultOptions={bound.value ? [bound.value] : undefined}
      getOptions={api.findDepots}
      normalize={norm.normalizeDepotOrUnknown}
      {...bound}
      {...props}
    />
  )
}

export const DeliverySiteCountryField = (props: AutocompleteProps<Country>) => {
  const { t } = useTranslation()
  const { value, bind } = useFormContext<LotFormValue>()
  const bound = bind("delivery_site_country")

  if (value.delivery_site instanceof Object) {
    return (
      <TextInput
        disabled
        readOnly={props.readOnly}
        label={t("Pays de livraison")}
        value={norm.normalizeCountry(value.delivery_site.country).label}
        error={bound.error}
      />
    )
  }

  return (
    <Autocomplete
      required
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
