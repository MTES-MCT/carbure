import { FormGroup } from "common/components/form"
import * as Fields from "./fields"
import { FieldsProps, isKnown } from "./fields"

const DeliveryFields = ({
  readOnly,
  entity,
  data,
  errors,
  onChange,
}: FieldsProps) => {
  const dsCountry = isKnown(data.delivery_site)
    ? data.delivery_site.country
    : data.delivery_site_country

  const isLotClient = isKnown(data.client) && entity?.id === data.client.id

  const showClient = !isLotClient || data.mac
  const showMAC = (readOnly && data.mac) || (!readOnly && entity?.has_mac)

  return (
    <FormGroup readOnly={readOnly} title="Livraison" onChange={onChange}>
      {showMAC && <Fields.Mac value={`${data.mac}`} />}
      {showClient && (
        <Fields.Client
          search={!data.mac}
          value={data.client}
          error={errors?.client}
        />
      )}
      <Fields.DeliverySite
        search={!data.mac}
        disabled={data.mac}
        value={data.delivery_site}
        error={errors?.delivery_site}
      />
      <Fields.DeliverySiteCountry
        disabled={isKnown(data.delivery_site) || data.mac}
        value={dsCountry}
        error={errors?.unknown_delivery_site_country}
      />
      <Fields.DeliveryDate
        value={data.delivery_date}
        error={errors?.delivery_date}
      />
    </FormGroup>
  )
}

export default DeliveryFields
