import { Autocomplete } from "common/components/autocomplete2"
import { useFormContext } from "common/components/form2"
import useEntity from "common/hooks/entity"
import { EntityPreview } from "common/types"
import { useTranslation } from "react-i18next"
import { findEligibleTiruertEntities } from "./api"
import { normalizeEntityPreview } from "common/utils/normalizers"
import { OperationText } from "../operation-text"
import { Step } from "common/components/stepper"
import i18next from "i18next"

export type RecipientFormProps = {
  credited_entity?: EntityPreview
}

export type RecipientFormComponentProps = {
  required?: boolean
}

export const RecipientForm = (overrides: RecipientFormComponentProps) => {
  const { t } = useTranslation()
  const { bind } = useFormContext<RecipientFormProps>()
  const entity = useEntity()

  return (
    <Autocomplete
      label={t("Destinataire")}
      placeholder={t("Rechercher un destinataire")}
      getOptions={(query) => findEligibleTiruertEntities(entity.id, query)}
      normalize={normalizeEntityPreview}
      {...bind("credited_entity")}
      required
      {...overrides}
    />
  )
}

export const RecipientSummary = ({
  values,
}: {
  values: RecipientFormProps
}) => {
  const { t } = useTranslation()

  if (!values.credited_entity) {
    return null
  }

  return (
    <OperationText
      title={t("Destinataire")}
      description={values.credited_entity.name}
    />
  )
}

export const showNextStepRecipientForm = (values: RecipientFormProps) => {
  return Boolean(values.credited_entity)
}

export const recipientStepKey = "recipient_to_depot"
type RecipientStepKey = typeof recipientStepKey

export const recipientStep: Step<RecipientStepKey> = {
  key: recipientStepKey,
  title: i18next.t("Destinataire"),
}
