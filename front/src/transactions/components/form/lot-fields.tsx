import { FormGroup } from "common/components/form"
import * as Fields from "./fields"
import { FieldsProps } from "./fields"

export const LotFields = ({
  readOnly,
  data,
  errors,
  onChange,
}: FieldsProps) => (
  <FormGroup readOnly={readOnly} title="Lot" onChange={onChange}>
    <Fields.Dae value={data.dae} error={errors?.dae} />
    <Fields.Volume value={data.volume} error={errors?.volume} />
    <Fields.Biocarburant
      value={data.biocarburant}
      error={errors?.biocarburant_code}
    />
    <Fields.MatierePremiere
      value={data.matiere_premiere}
      error={errors?.matiere_premiere_code}
    />
    <Fields.PaysOrigine
      value={data.pays_origine}
      error={errors?.pays_origine_code}
    />
  </FormGroup>
)

export default LotFields
