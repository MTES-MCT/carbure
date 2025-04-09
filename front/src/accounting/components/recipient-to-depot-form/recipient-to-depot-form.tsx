import { Autocomplete } from "common/components/autocomplete2"
import { useFormContext } from "common/components/form2"
import { findDepots } from "common/api"
import {
  normalizeDepot,
  normalizeEntityPreview,
} from "common/utils/normalizers"
import { useTranslation } from "react-i18next"
import { OperationText } from "accounting/components/operation-text"
import { findEligibleTiruertEntities } from "./api"
import useEntity from "common/hooks/entity"
import { Depot, EntityPreview } from "common/types"
import { Step } from "common/components/stepper"
import i18next from "i18next"

export type RecipientToDepotFormProps = {
  credited_entity?: EntityPreview
  to_depot?: Depot
}

export const RecipientToDepotForm = () => {
  const { t } = useTranslation()
  const { bind } = useFormContext<RecipientToDepotFormProps>()
  const entity = useEntity()

  return (
    <>
      <Autocomplete
        label={t("Sélectionnez un destinataire")}
        placeholder={t("Rechercher un destinataire")}
        getOptions={(query) => findEligibleTiruertEntities(entity.id, query)}
        normalize={normalizeEntityPreview}
        {...bind("credited_entity")}
        required
      />
      <Autocomplete
        label={t("Sélectionnez un dépôt destinataire")}
        placeholder={t("Rechercher un dépôt")}
        getOptions={findDepots}
        normalize={normalizeDepot}
        {...bind("to_depot")}
      />
    </>
  )
}

export const RecipientToDepotSummary = ({
  values,
  children,
}: {
  values: RecipientToDepotFormProps
  children?: React.ReactNode
}) => {
  const { t } = useTranslation()

  if (!values.credited_entity) {
    return null
  }

  return (
    <>
      <OperationText
        title={t("Destinataire")}
        description={values.credited_entity.name}
      />
      {values.to_depot && (
        <OperationText
          title={t("Dépôt destinataire")}
          description={values.to_depot?.name ?? ""}
        />
      )}
      {children}
    </>
  )
}

export const showNextStepRecipientToDepotForm = (
  values: RecipientToDepotFormProps
) => {
  return Boolean(values.credited_entity)
}

export const recipientToDepotStepKey = "recipient_to_depot"
type RecipientToDepotStepKey = typeof recipientToDepotStepKey

export const recipientToDepotStep: (
  values: RecipientToDepotFormProps
) => Step<RecipientToDepotStepKey> = (values) => ({
  key: recipientToDepotStepKey,
  title: i18next.t("Redevable et dépôt destinataire"),
  allowNextStep: showNextStepRecipientToDepotForm(values),
})
