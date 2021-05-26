import { FormGroup } from "common/components/form"
import * as Fields from "./fields"
import { FieldsProps } from "./fields"

export const LotFields = ({
  readOnly,
  data,
  errors,
  editable,
  onChange,
}: FieldsProps) => (
  <FormGroup
    readOnly={readOnly || !editable}
    title="Lot"
    data={data}
    errors={errors}
    onChange={onChange}
  >
    <Fields.Dae readOnly={readOnly} />
    <Fields.Volume readOnly={readOnly} />
    <Fields.Biocarburant />
    <Fields.MatierePremiere />
    <Fields.PaysOrigine />
  </FormGroup>
)

export default LotFields
