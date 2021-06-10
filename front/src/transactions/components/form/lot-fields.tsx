import { useTranslation } from "react-i18next"
import { FormGroup } from "common/components/form"
import * as Fields from "./fields"
import { FieldsProps } from "./fields"

export const LotFields = ({
  readOnly,
  data,
  errors,
  editable,
  onChange,
}: FieldsProps) => {
  const { t } = useTranslation()
  return (
    <FormGroup
      readOnly={readOnly || !editable}
      title={t("Lot")}
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
}

export default LotFields
