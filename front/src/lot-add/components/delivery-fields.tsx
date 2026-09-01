import { useTranslation } from "react-i18next"
import useEntity, { EntityManager } from "common/hooks/entity"
import { Fieldset, useBind, useFormContext } from "common/components/form"
import Autocomplete, { AutocompleteProps } from "common/components/autocomplete"
import {
  DateInput,
  DateInputProps,
  TextInput,
  TextInputProps,
} from "common/components/input"
import { UserCheck } from "common/components/icons"
import * as api from "common/api"
import * as norm from "common/utils/normalizers"
import { compact } from "common/utils/collection"
import { FuelUsageSelect } from "transactions/components/fuel-usage-select"
import { isExternalDelivery, LotFormValue } from "./lot-form"
import { LotStatus } from "transactions/types"
import { Country, Depot, EntityPreview } from "common/types"
import Select, { SelectProps } from "common/components/select"
import { DeliveryType, FuelUsage } from "transactions/types"

interface DeliveryFieldsProps {
  readOnly?: boolean
}

export const DeliveryFields = (props: DeliveryFieldsProps) => {
  const { t } = useTranslation()
  return (
    <Fieldset label={t("Livraison")}>
      <ClientField {...props} />
      <DeliveryTypeField {...props} />
      <UsageField {...props} />
      <UsagePrecisionField {...props} />
      <DeliverySiteField {...props} />
      <DeliverySiteCountryField {...props} />
      <DeliveryDateField {...props} />
    </Fieldset>
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

export const UsageField = (props: SelectProps<FuelUsage>) => {
  const { value, bind } = useFormContext<LotFormValue>()

  if (value.delivery_type !== DeliveryType.RFC) {
    return null
  }

  return <FuelUsageSelect required {...bind("usage")} {...props} />
}

export const UsagePrecisionField = (props: TextInputProps) => {
  const { t } = useTranslation()
  const { value, bind } = useFormContext<LotFormValue>()

  if (
    value.delivery_type !== DeliveryType.RFC ||
    value.usage !== FuelUsage.Other
  ) {
    return null
  }

  return (
    <TextInput
      required
      label={`${t("Précisions")}`}
      placeholder={t("Préciser l'usage")}
      {...bind("usage_precision")}
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
