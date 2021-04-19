import * as Fields from "./fields"
import { FieldsProps, isKnown } from "./fields"
import { FormGroup } from "common/components/form"

const ProductionFields = ({
  readOnly,
  entity,
  data,
  errors,
  onChange,
}: FieldsProps) => {
  const isLotProducer = isKnown(data.producer) && data.producer.id === entity?.id // prettier-ignore

  return (
    <FormGroup
      readOnly={readOnly}
      title="Production"
      data={data}
      errors={errors}
      onChange={onChange}
    >
      <Fields.ProductionSite search={isLotProducer} />
      <Fields.ProductionSiteReference />
      <Fields.ProductionSiteCountry />
      <Fields.ProductionSiteDblCounting />
      <Fields.ProductionSiteDate />
    </FormGroup>
  )
}

export default ProductionFields
