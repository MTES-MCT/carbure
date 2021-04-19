import { FormGroup } from "common/components/form"
import { EntityType } from "common/types"
import * as Fields from "./fields"
import { FieldsProps, isKnown } from "./fields"

export const ProducerOriginFields = ({
  entity,
  readOnly,
  data,
  onChange,
}: FieldsProps) => {
  async function listOnlyThisProducer(query: string) {
    return entity && entity.name.toLowerCase().startsWith(query.toLowerCase())
      ? [entity]
      : []
  }

  const isInCarbure = isKnown(data.producer)

  return (
    <FormGroup readOnly={readOnly} title="Provenance" onChange={onChange}>
      <Fields.Producer
        disabled={!entity?.has_trading}
        minLength={0}
        value={data.producer}
        getQuery={listOnlyThisProducer}
      />
      <Fields.UnknownSupplier
        disabled={isInCarbure}
        value={data.unknown_supplier ?? ""}
      />
      <Fields.UnknownSupplierCertificate
        disabled={isInCarbure}
        value={data.unknown_supplier_certificate ?? ""}
      />
      <Fields.CarbureSelfCertificate
        value={data.carbure_vendor_certificate ?? ""}
        queryArgs={[entity?.id]}
      />
      <Fields.ChampLibre value={data.champ_libre} />
    </FormGroup>
  )
}

export const OperatorOriginFields = ({
  readOnly,
  data,
  onChange,
}: FieldsProps) => {
  return (
    <FormGroup readOnly={readOnly} title="Provenance" onChange={onChange}>
      <Fields.Producer search={false} value={data.producer} />
      <Fields.UnknownSupplier value={data.unknown_supplier ?? ""} />
      <Fields.UnknownSupplierCertificate
        value={data.unknown_supplier_certificate ?? ""}
      />
      <Fields.ChampLibre value={data.champ_libre} />
    </FormGroup>
  )
}

export const VendorOriginFields = ({
  readOnly,
  entity,
  data,
  onChange,
}: FieldsProps) => {
  return (
    <FormGroup readOnly={readOnly} title="Provenance" onChange={onChange}>
      <Fields.Producer search={false} value={data.producer} />
      <Fields.UnknownSupplier value={data.unknown_supplier ?? ""} />
      <Fields.UnknownSupplierCertificate
        value={data.unknown_supplier_certificate ?? ""}
      />
      <Fields.CarbureSelfCertificate
        value={data.carbure_vendor_certificate ?? ""}
        queryArgs={[entity?.id]}
      />
      <Fields.ChampLibre value={data.champ_libre} />
    </FormGroup>
  )
}

export const ClientOriginFields = ({
  readOnly,
  data,
  onChange,
}: FieldsProps) => {
  return (
    <FormGroup readOnly={readOnly} title="Provenance" onChange={onChange}>
      <Fields.Producer value={data.producer} />
      <Fields.CarbureVendor value={data.carbure_vendor ?? ""} />
      <Fields.CarbureVendorCertificate
        value={data.carbure_vendor_certificate ?? ""}
      />
      <Fields.ChampLibre value={data.champ_libre} />
    </FormGroup>
  )
}

export const AdminOriginFields = ({
  readOnly,
  data,
  onChange,
}: FieldsProps) => {
  return (
    <FormGroup readOnly={readOnly} title="Provenance" onChange={onChange}>
      <Fields.Producer value={data.producer} />
      <Fields.UnknownSupplier
        value={data.unknown_supplier ?? ""}
        label="Fournisseur original"
      />
      <Fields.UnknownSupplierCertificate
        value={data.unknown_supplier_certificate ?? ""}
        label="Certificat fournisseur original"
      />
      <Fields.CarbureVendor value={data.carbure_vendor ?? ""} />
      <Fields.CarbureVendorCertificate
        value={data.carbure_vendor_certificate ?? ""}
      />
      <Fields.ChampLibre value={data.champ_libre} />
    </FormGroup>
  )
}

export default function OriginFields(props: FieldsProps) {
  const { entity, data } = props

  const isDraft = data.status === "Draft"

  const isProducer = entity?.entity_type === EntityType.Producer
  const isOperator = entity?.entity_type === EntityType.Operator
  const isTrader = entity?.entity_type === EntityType.Trader
  const isAdmin = entity?.entity_type === EntityType.Administration

  const isAuthor = entity?.id === data.added_by?.id
  const isVendor = isKnown(data.carbure_vendor) && entity?.id === data.carbure_vendor.id // prettier-ignore
  const isClient = isKnown(data.client) && entity?.id === data.client.id

  if (isAdmin) {
    return <AdminOriginFields {...props} />
  } else if (isDraft) {
    if (isProducer) {
      return <ProducerOriginFields {...props} />
    } else if (isOperator) {
      return <OperatorOriginFields {...props} />
    } else if (isTrader) {
      return <VendorOriginFields {...props} />
    }
  } else {
    if (isOperator && isAuthor) {
      return <OperatorOriginFields {...props} />
    } else if (isVendor || isAuthor) {
      return <VendorOriginFields {...props} />
    } else if (isClient) {
      return <ClientOriginFields {...props} />
    }
  }

  return null
}
