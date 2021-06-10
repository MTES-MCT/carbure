import { Fragment } from "react"
import { useTranslation } from "react-i18next"
import * as Fields from "./fields"
import { FieldsProps } from "./fields"
import { FormGroup } from "common/components/form"

const GESFields = (props: FieldsProps) => {
  const { t } = useTranslation()

  return (
    <Fragment>
      <FormGroup {...props} narrow title={t("Émissions")}>
        <Fields.Eec />
        <Fields.El />
        <Fields.Ep />
        <Fields.Etd />
        <Fields.Eu />
        <Fields.GhgTotal />
      </FormGroup>

      <FormGroup {...props} narrow title={t("Réductions")}>
        <Fields.Esca />
        <Fields.Eccs />
        <Fields.Eccr />
        <Fields.Eee />
        <Fields.GhgReduction />
      </FormGroup>
    </Fragment>
  )
}

export default GESFields
