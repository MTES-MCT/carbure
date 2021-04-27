import { Fragment } from "react"
import * as Fields from "./fields"
import { FieldsProps } from "./fields"
import { FormGroup } from "common/components/form"

const GESFields = (props: FieldsProps) => (
  <Fragment>
    <FormGroup {...props} narrow title="Émissions">
      <Fields.Eec />
      <Fields.El />
      <Fields.Ep />
      <Fields.Etd />
      <Fields.Eu />
      <Fields.GhgTotal />
    </FormGroup>

    <FormGroup {...props} narrow title="Réductions">
      <Fields.Esca />
      <Fields.Eccs />
      <Fields.Eccr />
      <Fields.Eee />
      <Fields.GhgReduction />
    </FormGroup>
  </Fragment>
)

export default GESFields
