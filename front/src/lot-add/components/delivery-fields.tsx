import { useTranslation } from "react-i18next"
import useEntity, { EntityManager } from "carbure/hooks/entity"
import { Fieldset, useBind, useFormContext } from "common-v2/components/form"
import Autocomplete, {
  AutocompleteProps,
} from "common-v2/components/autocomplete"
import {
  DateInput,
  DateInputProps,
  TextInput,
} from "common-v2/components/input"
import { UserCheck } from "common-v2/components/icons"
import * as api from "common-v2/api"
import * as norm from "common-v2/utils/normalizers"
import { LotFormValue } from "./lot-form"
import { Entity } from "carbure/types"
import { Country, Depot } from "common/types"
import Select, { SelectProps } from "common-v2/components/select"
import { DeliveryType } from "transactions/types"
import { compact } from "common-v2/utils/collection"

interface DeliveryFieldsProps {
  readOnly?: boolean
}

export const DeliveryFields = (props: DeliveryFieldsProps) => {
  const { t } = useTranslation()
  return (
    <Fieldset label={t("Livraison")}>
      <MyCertificateField {...props} />
      <SupplierField {...props} />
      <SupplierCertificateField {...props} />
      <ClientField {...props} />
      <DeliveryTypeField {...props} />
      <DeliverySiteField {...props} />
      <DeliverySiteCountryField {...props} />
      <DeliveryDateField {...props} />
    </Fieldset>
  )
}

export const SupplierField = (props: AutocompleteProps<Entity | string>) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const bind = useBind<LotFormValue>()

  const { value: supplier, ...bound } = bind("supplier")
  const isKnown = supplier instanceof Object

  return (
    <Autocomplete
      label={t("Fournisseur")}
      value={supplier}
      icon={isKnown ? UserCheck : undefined}
      create={norm.identity}
      defaultOptions={supplier ? [supplier] : [entity]}
      getOptions={async () => [entity]}
      normalize={norm.normalizeEntityOrUnknown}
      {...bound}
      {...props}
    />
  )
}

export const SupplierCertificateField = (props: AutocompleteProps<string>) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { value, bind } = useFormContext<LotFormValue>()
  const bound = bind("supplier_certificate")

  const supplier = value.supplier instanceof Object ? value.supplier : undefined
  const isSupplier = entity.id === supplier?.id

  return (
    <Autocomplete
      label={t("Certificat du fournisseur")}
      placeholder={supplier?.default_certificate}
      defaultOptions={bound.value ? [bound.value] : undefined}
      getOptions={(query) =>
        isSupplier
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

  const supplier = value.supplier instanceof Object ? value.supplier : undefined
  const client = value.client instanceof Object ? value.client : undefined

  // hide this field if this entity is NOT an intermediary
  // or if the supplier and client are not defined
  if (
    supplier?.id === entity.id ||
    client?.id === entity.id ||
    !value.supplier ||
    !value.client
  ) {
    return null
  }

  return (
    <Autocomplete
      label={t("Votre certificat")}
      placeholder={entity?.default_certificate}
      defaultOptions={bound.value ? [bound.value] : undefined}
      getOptions={(query) =>
        api.findMyCertificates(query, { entity_id: entity.id })
      }
      {...bound}
      {...props}
    />
  )
}

export const ClientField = (props: AutocompleteProps<Entity | string>) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const bind = useBind<LotFormValue>()
  const bound = bind("client")
  const isKnown = bound.value instanceof Object

  return (
    <Autocomplete
      disabled={entity.isOperator && !entity.has_mac}
      label={t("Client")}
      placeholder={entity.isOperator ? entity.name : undefined}
      icon={isKnown ? UserCheck : undefined}
      create={norm.identity}
      defaultOptions={bound.value ? [bound.value] : undefined}
      getOptions={api.findEntities}
      normalize={norm.normalizeEntityOrUnknown}
      {...bound}
      {...props}
    />
  )
}

// DeliveryType field should only appear when the client is either the current entity or an unknown one
export const DeliveryTypeField = (props: SelectProps<DeliveryType>) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { value, bind } = useFormContext<LotFormValue>()
  const deliveryTypes = getDeliveryTypes(entity, value.client)

  if (deliveryTypes.length === 0) {
    return null
  }

  return (
    <Select
      clear
      label={t("Type de livraison")}
      placeholder={t("Choisissez un type")}
      normalize={norm.normalizeDeliveryType}
      options={deliveryTypes}
      {...bind("delivery_type")}
      {...props}
    />
  )
}

export function getDeliveryTypes(
  entity: EntityManager,
  client: Entity | string | undefined
) {
  const { isOperator, has_stocks, has_mac, has_direct_deliveries } = entity
  const isClientEntity = client instanceof Object ? client.id === entity.id : false // prettier-ignore
  const isClientUnknown = client === undefined || typeof client === "string"

  return compact([
    isClientEntity && isOperator && DeliveryType.Blending,
    isClientEntity && has_stocks && DeliveryType.Stock,
    isClientUnknown && has_mac && DeliveryType.RFC,
    isClientUnknown && has_direct_deliveries && DeliveryType.Direct,
    isClientUnknown && DeliveryType.Export,
  ])
}

export const DeliverySiteField = (props: AutocompleteProps<Depot | string>) => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  const bound = bind("delivery_site")
  const isKnown = bound.value instanceof Object

  return (
    <Autocomplete
      label={t("Site de livraison")}
      icon={isKnown ? UserCheck : undefined}
      create={norm.identity}
      defaultOptions={bound.value ? [bound.value] : undefined}
      getOptions={api.findDepots}
      normalize={norm.normalizeDepot}
      {...bound}
      {...props}
    />
  )
}

export const DeliverySiteCountryField = (props: AutocompleteProps<Country>) => {
  const { t } = useTranslation()
  const { value, bind } = useFormContext<LotFormValue>()

  if (value.delivery_site instanceof Object) {
    return (
      <TextInput
        disabled
        label={t("Pays de livraison")}
        value={norm.normalizeCountry(value.delivery_site.country).label}
      />
    )
  }

  const bound = bind("delivery_site_country")
  return (
    <Autocomplete
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
