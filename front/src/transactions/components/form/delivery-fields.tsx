import { EntitySelection } from "carbure/hooks/use-entity"
import { FormGroup } from "common/components/form"
import { EntityType } from "common/types"
import { TransactionFormState } from "transactions/hooks/use-transaction-form"
import * as Fields from "./fields"
import { FieldsProps, isKnown } from "./fields"

function showMAC(data: TransactionFormState, entity?: EntitySelection) {
  return (data.status === "Draft" && entity?.has_mac) || data.mac
}

const AllDeliveryFields = ({ data, errors, onChange }: FieldsProps) => {
  return (
    <FormGroup
      readOnly
      title="Livraison"
      data={data}
      errors={errors}
      onChange={onChange}
    >
      {data.mac && <Fields.Mac />}
      <Fields.CarbureVendor />
      <Fields.CarbureVendorCertificate />
      <Fields.Client />
      <Fields.DeliverySite />
      <Fields.DeliverySiteCountry />
      <Fields.DeliveryDate />
    </FormGroup>
  )
}

const VendorDeliveryFields = ({
  data,
  errors,
  entity,
  readOnly,
  onChange,
}: FieldsProps) => {
  return (
    <FormGroup
      readOnly={readOnly}
      title="Livraison"
      data={data}
      errors={errors}
      onChange={onChange}
    >
      {showMAC(data, entity) && <Fields.Mac />}
      <Fields.CarbureSelfCertificate />
      <Fields.Client />
      <Fields.DeliverySite />
      <Fields.DeliverySiteCountry />
      <Fields.DeliveryDate />
    </FormGroup>
  )
}

const ClientDeliveryFields = ({
  data,
  errors,
  entity,
  readOnly,
  onChange,
}: FieldsProps) => {
  const isOperator = entity?.entity_type === EntityType.Operator

  return (
    <FormGroup
      readOnly={readOnly}
      title="Livraison"
      data={data}
      errors={errors}
      onChange={onChange}
    >
      {showMAC(data, entity) && <Fields.Mac />}
      <Fields.Client disabled={isOperator && !data.mac} />
      <Fields.DeliverySite />
      <Fields.DeliverySiteCountry />
      <Fields.DeliveryDate />
    </FormGroup>
  )
}

export default function DeliveryFields(props: FieldsProps) {
  const { entity, data } = props

  const isOperator = entity?.entity_type === EntityType.Operator
  const isAdmin = entity?.entity_type === EntityType.Administration

  const isAuthor = entity?.id === data.added_by?.id
  const isClient = isKnown(data.client) && entity?.id === data.client.id // prettier-ignore
  const isVendor = isKnown(data.carbure_vendor) && entity?.id === data.carbure_vendor.id // prettier-ignore

  if (isAdmin) {
    return <AllDeliveryFields {...props} />
  } else if (isClient || isOperator) {
    return <ClientDeliveryFields {...props} />
  } else if (isVendor) {
    return <VendorDeliveryFields {...props} />
  } else if (isAuthor) {
    // this is for original authors of lots that were forwarded by their client
    return <AllDeliveryFields {...props} />
  }

  return null
}
