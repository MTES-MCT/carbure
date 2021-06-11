import * as Fields from "./fields"
import { FieldsProps } from "./fields"
import { FormGroup } from "common/components/form"
import { EntityType } from "common/types"
import { useTranslation } from "react-i18next"

const ProductionFields = ({
  readOnly,
  entity,
  data,
  errors,
  onChange,
}: FieldsProps) => {
  const { t } = useTranslation()
  const isProducer = entity?.entity_type === EntityType.Producer // prettier-ignore

  return (
    <FormGroup
      readOnly={readOnly}
      title={t("Production")}
      data={data}
      errors={errors}
      onChange={onChange}
    >
      <Fields.ProductionSite search={isProducer} queryArgs={[entity?.id]} />
      <Fields.ProductionSiteReference />
      <Fields.ProductionSiteCountry />
      <Fields.ProductionSiteDblCounting />
      <Fields.ProductionSiteDate />
    </FormGroup>
  )
}

export default ProductionFields
