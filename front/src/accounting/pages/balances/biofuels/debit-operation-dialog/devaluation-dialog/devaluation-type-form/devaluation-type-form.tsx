import { OperationText } from "accounting/components/operation-text"
import { DevaluationType } from "accounting/types"
import { formatDevaluationType } from "accounting/utils/formatters"
import { useFormContext } from "common/components/form2"
import { Select } from "common/components/selects2"
import { useTranslation } from "react-i18next"
import { DevaluationTypeFormProps } from "./devaluation-type-form.types"

export const DevaluationTypeForm = () => {
  const { t } = useTranslation()
  const { bind } = useFormContext<DevaluationTypeFormProps>()

  return (
    <Select
      variant="form"
      label={t("Type de dévalorisation")}
      options={[
        {
          label: formatDevaluationType(DevaluationType.LOSS),
          value: DevaluationType.LOSS,
        },
        {
          label: formatDevaluationType(DevaluationType.DOWNGRADING),
          value: DevaluationType.DOWNGRADING,
        },
        {
          label: formatDevaluationType(DevaluationType.OTHER),
          value: DevaluationType.OTHER,
        },
      ]}
      {...bind("devaluation_type")}
      required
    />
  )
}

// Recap form data after the step was submitted
export const DevaluationTypeSummary = ({
  values,
}: {
  values: DevaluationTypeFormProps
}) => {
  const { t } = useTranslation()

  if (!values.devaluation_type) {
    return null
  }

  return (
    <OperationText
      title={t("Type de dévalorisation")}
      description={formatDevaluationType(values.devaluation_type)}
    />
  )
}
