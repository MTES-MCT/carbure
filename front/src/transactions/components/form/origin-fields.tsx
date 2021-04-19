import { FormGroup } from "common/components/form"
import { EntityType } from "common/types"
import * as Fields from "./fields"
import { FieldsProps, isKnown } from "./fields"

export const AdminOriginFields = ({ data, errors, onChange }: FieldsProps) => {
  return (
    <FormGroup
      readOnly
      title="Provenance"
      data={data}
      errors={errors}
      onChange={onChange}
    >
      <Fields.Producer search={false} />
      <Fields.UnknownSupplier label="Fournisseur original" />
      <Fields.UnknownSupplierCertificate label="Certificat fournisseur original" />
      <Fields.ChampLibre />
    </FormGroup>
  )
}

export const ProducerOriginFields = ({
  entity,
  readOnly,
  data,
  errors,
  stock,
  onChange,
}: FieldsProps) => {
  async function listOnlyThisProducer(query: string) {
    const entityLow = entity?.name.toLowerCase()
    const queryLow = query.toLowerCase()
    return entity && entityLow?.startsWith(queryLow) ? [entity] : []
  }

  return (
    <FormGroup
      readOnly={stock || readOnly}
      title="Provenance"
      data={data}
      errors={errors}
      onChange={onChange}
    >
      <Fields.Producer
        disabled={!entity?.has_trading}
        getQuery={listOnlyThisProducer}
      />
      <Fields.UnknownSupplier />
      <Fields.UnknownSupplierCertificate />
      <Fields.ChampLibre />
    </FormGroup>
  )
}

export const AuthorOriginFields = ({
  readOnly,
  data,
  errors,
  stock,
  onChange,
}: FieldsProps) => {
  return (
    <FormGroup
      readOnly={stock || readOnly}
      title="Provenance"
      data={data}
      errors={errors}
      onChange={onChange}
    >
      <Fields.Producer search={false} />
      <Fields.UnknownSupplier />
      <Fields.UnknownSupplierCertificate />
      <Fields.ChampLibre />
    </FormGroup>
  )
}

export const ClientOriginFields = ({
  readOnly,
  data,
  errors,
  onChange,
}: FieldsProps) => {
  return (
    <FormGroup
      readOnly={readOnly}
      title="Provenance"
      data={data}
      errors={errors}
      onChange={onChange}
    >
      <Fields.Producer search={false} />
      <Fields.CarbureVendor />
      <Fields.CarbureVendorCertificate />
      <Fields.ChampLibre />
    </FormGroup>
  )
}

export default function OriginFields(props: FieldsProps) {
  const { entity, data } = props

  // lot is draft or entity is author
  const canEdit = data.status === "Draft" || entity?.id === data.added_by?.id

  const isProducer = entity?.entity_type === EntityType.Producer
  const isAdmin = entity?.entity_type === EntityType.Administration

  const isVendor = isKnown(data.carbure_vendor) && entity?.id === data.carbure_vendor.id // prettier-ignore
  const isClient = isKnown(data.client) && entity?.id === data.client.id

  if (isAdmin) {
    return <AdminOriginFields {...props} />
  } else if (isProducer && canEdit) {
    return <ProducerOriginFields {...props} />
  } else if (isVendor || canEdit) {
    return <AuthorOriginFields {...props} />
  } else if (isClient) {
    return <ClientOriginFields {...props} />
  }

  return null
}
