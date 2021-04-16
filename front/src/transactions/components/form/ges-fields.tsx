import { Fragment } from "react"
import * as Fields from "./fields"
import { FieldsProps } from "./fields"
import { FormGroup } from "common/components/form"

const GESFields = ({ readOnly, data, onChange }: FieldsProps) => (
  <Fragment>
    <FormGroup narrow readOnly={readOnly} title="Émissions" onChange={onChange}>
      <Fields.Eec value={data.eec} />
      <Fields.El value={data.el} />
      <Fields.Ep value={data.ep} />
      <Fields.Etd value={data.etd} />
      <Fields.Eu value={data.eu} />
      <Fields.GhgTotal value={data.ghg_total} />
    </FormGroup>

    <FormGroup
      narrow
      readOnly={readOnly}
      title="Réductions"
      onChange={onChange}
    >
      <Fields.Esca value={data.esca} />
      <Fields.Eccs value={data.eccs} />
      <Fields.Eccr value={data.eccr} />
      <Fields.Eee value={data.eee} />
      <Fields.GhgReduction value={data.ghg_reduction} />
    </FormGroup>
  </Fragment>
)

export default GESFields
