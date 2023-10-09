import { useEffect, useMemo } from "react"
import { useTranslation } from "react-i18next"
import useEntity from "carbure/hooks/entity"
import { DeliveryType, Lot, LotError } from "transactions/types"
import {
  Entity,
  Biofuel,
  Country,
  Depot,
  Feedstock,
  ProductionSite,
  Unit,
} from "carbure/types"
import Form, { FormErrors, FormManager, useForm } from "common/components/form"
import LotFields from "./lot-fields"
import ProductionFields from "./production-fields"
import DeliveryFields from "./delivery-fields"
import { EmissionFields, ReductionFields } from "./ghg-fields"
import { LotCertificates } from "transaction-details/types"
import { matches } from "common/utils/collection"

export interface LotFormProps {
  readOnly?: boolean
  form: FormManager<LotFormValue>
  novalidate?: boolean
  onSubmit?: (value?: LotFormValue) => void
}

export const LotForm = ({
  form,
  onSubmit,
  novalidate,
  ...props
}: LotFormProps) => (
  <Form
    id="lot-form"
    variant="columns"
    form={form}
    onSubmit={onSubmit}
    novalidate={novalidate}
  >
    <LotFields {...props} />
    <ProductionFields {...props} />
    <DeliveryFields {...props} />
    <EmissionFields {...props} />
    <ReductionFields {...props} />
  </Form>
)

const GHG_REFERENCE = 83.8
const GHG_REFERENCE_RED_II = 94.0

export function useLotForm(
  lot?: Lot | undefined,
  lotErrors: LotError[] = [],
  certs?: LotCertificates
) {
  const entity = useEntity()
  const value = useMemo(
    () => lotToFormValue(lot, entity, certs),
    [lot, entity, certs]
  )
  const errors = useLotFieldErrors(lotErrors)

  function setValue(value: LotFormValue): LotFormValue {
    if (entity.isAdmin) return value
    if (value.lot && value.lot.lot_status !== "DRAFT") return value

    // for producers
    if (entity.isProducer) {
      if (isLotProducer(entity, value) && value.supplier === undefined) {
        value.supplier = entity
      }

      if (!entity.has_trading && !entity.has_stocks) {
        value.producer = entity
      }
    }

    // for operators
    if (entity.isOperator) {
      if (value.client === undefined) {
        value.client = entity
      }
    }

    // automatically set the default certificate of the supplier
    if (
      isLotSupplier(entity, value) &&
      value.supplier_certificate === undefined
    ) {
      value.supplier_certificate = entity.default_certificate
      value.vendor_certificate = undefined
    }

    if (isLotVendor(entity, value) && value.vendor_certificate === undefined) {
      value.vendor_certificate = entity.default_certificate
    }

    const knownClient =
      value.client instanceof Object ? value.client : undefined
    const isClientEntity = knownClient?.id === entity.id
    const isClientUnknown = knownClient === undefined

    if (!isClientEntity && !isClientUnknown) {
      value.delivery_type = undefined
    }

    // update GES summary
    const total = computeGHGTotal(value)
    const reduction = computeGHGReduction(total, GHG_REFERENCE)
    const reductionRedII = computeGHGReduction(total, GHG_REFERENCE_RED_II)

    value.ghg_total = total
    value.ghg_reduction = reduction
    value.ghg_reduction_red_ii = reductionRedII

    return value
  }

  const form = useForm(setValue(value), { errors, setValue })

  // update the form when the loaded lot changes
  const updateForm = form.setValue
  useEffect(() => updateForm(value), [value, updateForm])

  const setDisabledFieldsGroup = (
    fieldGroups: FieldGroup[],
    otherFields?: string[]
  ) => {
    disabledFieldsGroup(form, fieldGroups)
    if (otherFields) {
      form.setDisabledFields(otherFields)
    }
  }

  return {
    setDisabledFieldsGroup,
    ...form,
  }
}

const BATCH_VALUES = [
  "volume",
  "transport_document_reference",
  "biofuel",
  "feedstock",
  "country_of_origin",
]

const BATCH_PRODUCTION = [
  "producer",
  "production_site",
  "production_site_certificate",
  "production_country",
  "production_site_commissioning_date",
]

const BATCH_DELIVERY = [
  "supplier",
  "supplier_certificate",
  "client",
  "delivery_type",
  "delivery_site",
  "delivery_site_country",
  "delivery_date",
]

const BATCH_EMISSIONS = [
  "eccr",
  "eccs",
  "eec",
  "eee",
  "el",
  "ep",
  "esca",
  "etd",
  "eu",
]

export type FieldGroup = "batch" | "production" | "delivery" | "emissions"
const disabledFieldsGroup = (
  form: FormManager<LotFormValue>,
  fieldGroups: FieldGroup[]
) => {
  let values: string[] = []

  if (fieldGroups.includes("batch")) values.push(...BATCH_VALUES)
  if (fieldGroups.includes("production")) values.push(...BATCH_PRODUCTION)
  if (fieldGroups.includes("delivery")) values.push(...BATCH_DELIVERY)
  if (fieldGroups.includes("emissions")) values.push(...BATCH_EMISSIONS)

  form.setDisabledFields(values)
}

function computeGHGTotal(value: LotFormValue) {
  const {
    eec = 0,
    el = 0,
    ep = 0,
    etd = 0,
    eu = 0,
    esca = 0,
    eccs = 0,
    eccr = 0,
    eee = 0,
  } = value
  return eec + el + ep + etd + eu - esca - eccs - eccr - eee
}

function computeGHGReduction(total: number, reference: number) {
  return (1.0 - total / reference) * 100.0
}

export function useLotFieldErrors(
  errors: LotError[]
): FormErrors<LotFormValue> {
  const { t } = useTranslation()
  const fieldErrors: { [k: string]: string } = {}

  errors.forEach(({ error }) =>
    (errorsToFields[error] ?? []).forEach((field) => {
      const all = [fieldErrors[field], t(error, { ns: "errors" })]
      fieldErrors[field] = all.filter(Boolean).join(", ")
    })
  )

  return fieldErrors
}

export const defaultLot = {
  // save the whole Lot data so we can access it in the form
  lot: undefined as Lot | undefined,
  certificates: undefined as LotCertificates | undefined,

  transport_document_reference: undefined as string | undefined,
  volume: undefined as number | undefined,
  weight: undefined as number | undefined,
  lhv_amount: undefined as number | undefined,
  unit: "l" as Unit | undefined,
  biofuel: undefined as Biofuel | undefined,
  feedstock: undefined as Feedstock | undefined,
  country_of_origin: undefined as Country | undefined,
  free_field: undefined as string | undefined,

  producer: undefined as Entity | string | undefined,
  production_site: undefined as ProductionSite | string | undefined,
  production_site_certificate: undefined as string | undefined,
  production_country: undefined as Country | undefined,
  production_site_double_counting_certificate: undefined as string | undefined,
  production_site_commissioning_date: undefined as string | undefined,

  supplier: undefined as Entity | string | undefined,
  supplier_certificate: undefined as string | undefined,
  vendor_certificate: undefined as string | undefined,
  client: undefined as Entity | string | undefined,
  delivery_type: undefined as DeliveryType | undefined,
  delivery_site: undefined as Depot | string | undefined,
  delivery_site_country: undefined as Country | undefined,
  delivery_date: undefined as string | undefined,

  eec: 0 as number | undefined,
  el: 0 as number | undefined,
  ep: 0 as number | undefined,
  etd: 0 as number | undefined,
  eu: 0 as number | undefined,

  esca: 0 as number | undefined,
  eccs: 0 as number | undefined,
  eccr: 0 as number | undefined,
  eee: 0 as number | undefined,

  ghg_total: 0 as number | undefined,
  ghg_reduction: 0 as number | undefined,
  ghg_reduction_red_ii: 0 as number | undefined,
}

export type LotFormValue = typeof defaultLot

type LotToFormValue = (lot: Lot | undefined, entity: Entity, certificates?: LotCertificates) => LotFormValue // prettier-ignore
export const lotToFormValue: LotToFormValue = (lot, entity, certificates) => ({
  lot,
  certificates,

  transport_document_reference: lot?.transport_document_reference ?? undefined,
  volume: lot?.volume ?? undefined,
  weight: lot?.weight ?? undefined,
  lhv_amount: lot?.lhv_amount ?? undefined,
  unit: entity.preferred_unit ?? undefined,
  biofuel: lot?.biofuel ?? undefined,
  feedstock: lot?.feedstock ?? undefined,
  country_of_origin: lot?.country_of_origin ?? undefined,
  free_field: lot?.free_field?.replace("\n", ", ") ?? undefined,

  producer: lot?.carbure_producer ?? lot?.unknown_producer ?? undefined,
  production_site:
    lot?.carbure_production_site ?? lot?.unknown_production_site ?? undefined,
  production_country: lot?.production_country ?? undefined,
  production_site_certificate: lot?.production_site_certificate ?? undefined,
  production_site_commissioning_date:
    lot?.production_site_commissioning_date ?? undefined,
  production_site_double_counting_certificate:
    lot?.production_site_double_counting_certificate ?? undefined,

  supplier: lot?.carbure_supplier ?? lot?.unknown_supplier ?? undefined,
  supplier_certificate: lot?.supplier_certificate ?? undefined,
  vendor_certificate: lot?.vendor_certificate ?? undefined,
  client: lot?.carbure_client ?? lot?.unknown_client ?? undefined,
  delivery_type:
    lot?.delivery_type === "UNKNOWN" ? undefined : lot?.delivery_type,
  delivery_site:
    lot?.carbure_delivery_site ?? lot?.unknown_delivery_site ?? undefined,
  delivery_site_country: lot?.delivery_site_country ?? undefined,
  delivery_date: lot?.delivery_date ?? undefined,

  eec: lot?.eec ?? 0,
  el: lot?.el ?? 0,
  ep: lot?.ep ?? 0,
  etd: lot?.etd ?? 0,
  eu: lot?.eu ?? 0,

  esca: lot?.esca ?? 0,
  eccs: lot?.eccs ?? 0,
  eccr: lot?.eccr ?? 0,
  eee: lot?.eee ?? 0,

  ghg_total: lot?.ghg_total ?? 0,
  ghg_reduction: lot?.ghg_reduction ?? 0,
  ghg_reduction_red_ii: lot?.ghg_reduction_red_ii ?? 0,
})

export function lotFormToPayload(lot: Partial<LotFormValue> | undefined) {
  if (lot === undefined) return {}

  const unit = lot.unit ?? "l"

  const unitToField = {
    l: "volume" as "volume",
    kg: "weight" as "weight",
    MJ: "lhv_amount" as "lhv_amount",
  }

  // use preferred unit as default quantity to send to the api
  const quantity = lot[unitToField[unit]]

  return {
    transport_document_type: undefined,
    transport_document_reference: lot.transport_document_reference,
    quantity: quantity,
    unit: quantity === undefined ? undefined : unit,
    biofuel_code: lot.biofuel?.code,
    feedstock_code: lot.feedstock?.code,
    country_code: lot.country_of_origin?.code_pays,
    free_field: lot.free_field,

    eec: lot.eec,
    el: lot.el,
    ep: lot.ep,
    etd: lot.etd,
    eu: lot.eu,
    esca: lot.esca,
    eccs: lot.eccs,
    eccr: lot.eccr,
    eee: lot.eee,

    // production
    carbure_producer_id:
      lot.producer instanceof Object ? lot.producer.id : undefined,
    unknown_producer:
      typeof lot.producer === "string" ? lot.producer : undefined,
    carbure_production_site:
      lot.production_site instanceof Object
        ? lot.production_site.name
        : undefined,
    unknown_production_site:
      typeof lot.production_site === "string" ? lot.production_site : undefined,
    production_site_certificate: lot.production_site_certificate,
    production_site_certificate_type: undefined,
    production_country_code: lot.production_country?.code_pays,
    production_site_commissioning_date: lot.production_site_commissioning_date,
    production_site_double_counting_certificate:
      lot.production_site_double_counting_certificate,

    // supplier
    carbure_supplier_id:
      lot.supplier instanceof Object ? lot.supplier.id : undefined,
    unknown_supplier:
      typeof lot.supplier === "string" ? lot.supplier : undefined,
    supplier_certificate: lot.supplier_certificate,
    supplier_certificate_type: undefined,
    vendor_certificate: lot.vendor_certificate,
    vendor_certificate_type: undefined,

    // delivery
    delivery_type: lot.delivery_type,
    delivery_date: lot.delivery_date,
    carbure_client_id: lot.client instanceof Object ? lot.client.id : undefined,
    unknown_client: typeof lot.client === "string" ? lot.client : undefined,
    carbure_delivery_site_depot_id:
      lot.delivery_site instanceof Object
        ? lot.delivery_site.depot_id
        : undefined,
    unknown_delivery_site:
      typeof lot.delivery_site === "string" ? lot.delivery_site : undefined,
    delivery_site_country_code: lot.delivery_site_country?.code_pays,
  }
}

export function isExternalDelivery(value: LotFormValue) {
  return (
    value.delivery_type &&
    [DeliveryType.Exportation, DeliveryType.RFC, DeliveryType.Direct].includes(
      value.delivery_type
    )
  )
}

// tells if the entity is an intermediate in the transaction
export function isLotVendor(entity: Entity, value: LotFormValue) {
  const isSupplier = isLotSupplier(entity, value)
  const hasSupplier = !!value.supplier

  const isClient = isLotClient(entity, value)
  const hasClient = !!value.client

  return (!isSupplier && !isClient) || (!hasSupplier && !hasClient)
}

export function isLotClient(entity: Entity, value: LotFormValue) {
  const client = value.client instanceof Object ? value.client : undefined
  return client?.id === entity.id
}

export function isLotSupplier(entity: Entity, value: LotFormValue) {
  const supplier = value.supplier instanceof Object ? value.supplier : undefined
  return supplier?.id === entity.id
}

export function isLotProducer(
  entity: Entity,
  value: LotFormValue,
  withTrading?: boolean
) {
  const producer = value.producer instanceof Object ? value.producer : undefined
  const isProducerEntity = producer?.id === entity.id
  const hasTrading = !!producer?.has_stocks && !!producer.has_trading
  return withTrading ? isProducerEntity && hasTrading : isProducerEntity
}

// check if the content of the form has changed compared to the data loaded from the api
export function hasChange(
  form: LotFormValue | undefined,
  lot: Lot | undefined,
  entity: Entity
) {
  const formPayload = lotFormToPayload(form)
  const lotPayload = lotFormToPayload(lotToFormValue(lot, entity))
  return matches(formPayload, lotPayload)
}

// prettier-ignore
const errorsToFields: Record<string, (keyof LotFormValue)[]> = {
  BC_NOT_CONFIGURED: ["biofuel"],
  DEPRECATED_MP: ["feedstock"],
  GHG_EEC_0: ["eec"],
  GHG_EP_0: ["ep"],
  GHG_ETD_0: ["etd"],
  GHG_REDUC_INF_50: ["ghg_reduction", "ghg_reduction_red_ii"],
  GHG_REDUC_INF_60: ["ghg_reduction", "ghg_reduction_red_ii"],
  GHG_REDUC_INF_65: ["ghg_reduction", "ghg_reduction_red_ii"],
  GHG_REDUC_SUP_100: ["ghg_reduction", "ghg_reduction_red_ii"],
  GHG_REDUC_SUP_99: ["ghg_reduction", "ghg_reduction_red_ii"],
  INCORRECT_DELIVERY_DATE: ["delivery_date"],
  INCORRECT_DELIVERY_SITE_COUNTRY: ["delivery_site_country"],
  INCORRECT_FORMAT_DELIVERY_DATE: ['delivery_date'],
  MAC_BC_WRONG: ['biofuel'],
  MISSING_BIOFUEL: ['biofuel'],
  MISSING_CARBURE_CLIENT: ['client'],
  MISSING_CARBURE_DELIVERY_SITE: ['delivery_site'],
  MISSING_COUNTRY: ['delivery_site_country'],
  MISSING_DAE: ['transport_document_reference'],
  MISSING_DELIVERY_DATE: ['delivery_date'],
  MISSING_DELIVERY_SITE: ['delivery_site'],
  MISSING_FEEDSTOCK: ['feedstock'],
  MISSING_FEEDSTOCK_COUNTRY_OF_ORIGIN: ['country_of_origin'],
  MISSING_PRODSITE_CERTIFICATE: ['production_site_certificate'],
  MISSING_PRODUCTION_SITE_COMDATE: ['production_site_commissioning_date'],
  MISSING_REF_DBL_COUNTING: ['production_site_double_counting_certificate'],
  MISSING_SUPPLIER_CERTIFICATE: ['supplier_certificate'],
  MISSING_UNKNOWN_CLIENT: ['client'],
  MISSING_UNKNOWN_DELIVERY_SITE: ['delivery_site'],
  MISSING_UNKNOWN_DELIVERY_SITE_COUNTRY: ['delivery_site_country'],
  MISSING_DELIVERY_SITE_COUNTRY: ['delivery_site_country'],
  MISSING_TRANSPORT_DOCUMENT_REFERENCE: ["transport_document_reference"],
  MISSING_VOLUME: ['volume'],
  MP_BC_INCOHERENT: ['feedstock', 'biofuel'],
  MP_NOT_CONFIGURED: ['feedstock'],
  DEPOT_NOT_CONFIGURED: ['delivery_site'],
  PRODUCTION_SITE_COMDATE_FORMAT_INCORRECT: ['production_site_commissioning_date'],
  PROVENANCE_MP: ['country_of_origin'],
  UNKNOWN_BIOFUEL: ['biofuel'],
  UNKNOWN_CLIENT: ['client'],
  UNKNOWN_COUNTRY: ['delivery_site_country'],
  UNKNOWN_FEEDSTOCK: ['feedstock'],
  UNKNOWN_PRODUCTION_SITE: ['production_site'],
  VOLUME_FAIBLE: ['volume'],
  VOLUME_FORMAT_INCORRECT: ['volume'],
  VOLUME_LTE_0: ['volume'],
  WRONG_DELIVERY_DATE: ['delivery_date'],
  WRONG_PRODUCTION_SITE_COUNTRY: ['production_country'],
  NO_PRODSITE_CERT: ['production_site_certificate'],
  NO_SUPPLIER_CERT: ['supplier_certificate'],
  NO_VENDOR_CERT: ['supplier_certificate'],
  UNKNOWN_PRODSITE_CERT: ['production_site_certificate'],
  UNKNOWN_SUPPLIER_CERT: ['supplier_certificate'],
  UNKNOWN_VENDOR_CERT: ['supplier_certificate'],
  EXPIRED_PRODSITE_CERT: ['production_site_certificate'],
  EXPIRED_SUPPLIER_CERT: ['supplier_certificate'],
  EXPIRED_VENDOR_CERT: ['supplier_certificate'],
  UNKNOWN_DAE_FORMAT: ['transport_document_reference'],
  UNKNOWN_DOUBLE_COUNTING_CERTIFICATE: ['production_site_double_counting_certificate'],
  EXPIRED_DOUBLE_COUNTING_CERTIFICATE: ['production_site_double_counting_certificate'],
  INVALID_DOUBLE_COUNTING_CERTIFICATE: ['production_site_double_counting_certificate'],
  MISSING_VENDOR_CERTIFICATE: ['vendor_certificate']
}

export default LotForm
