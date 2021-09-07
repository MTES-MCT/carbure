import { Fragment } from "react"
import isAfter from "date-fns/isAfter"
import { useTranslation } from "react-i18next"
import * as Fields from "./fields"
import { FieldsProps } from "./fields"
import { FormGroup } from "common/components/form"

// date where RED II took effect
const JULY_FIRST = new Date("2021-07-01")

const GESFields = (props: FieldsProps) => {
  const { t } = useTranslation()

  const date = new Date(props.data.delivery_date)
  const isRedII = isAfter(date, JULY_FIRST)

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
        {isRedII && <Fields.GhgReductionRed2 />}
      </FormGroup>
    </Fragment>
  )
}

export default GESFields
