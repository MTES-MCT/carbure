import { Autocomplete } from "common/components/autocomplete2"
import { useFormContext } from "common/components/form2"
import { findDepots } from "common/api"
import {
  normalizeDepot,
  normalizeEntityPreview,
} from "common/utils/normalizers"
import { useTranslation } from "react-i18next"
import { Grid } from "common/components/scaffold"
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
        label={t("Sélectionnez un redevable")}
        getOptions={(query) => findEligibleTiruertEntities(entity.id, query)}
        normalize={normalizeEntityPreview}
        {...bind("credited_entity")}
        required
      />
      <Autocomplete
        label={t("Sélectionnez un dépôt destinataire")}
        getOptions={findDepots}
        normalize={normalizeDepot}
        {...bind("to_depot")}
      />
    </>
  )
}

export const RecipientToDepotSummary = ({
  values,
}: {
  values: RecipientToDepotFormProps
}) => {
  const { t } = useTranslation()

  if (!values.credited_entity) {
    return null
  }

  return (
    <Grid>
      <OperationText
        title={t("Redevable")}
        description={values.credited_entity.name}
      />
      {values.to_depot && (
        <OperationText
          title={t("Dépôt destinataire")}
          description={values.to_depot?.name ?? ""}
        />
      )}
    </Grid>
  )
}

const showNextStepRecipientToDepotForm = (
  values: RecipientToDepotFormProps
) => {
  return Boolean(values.credited_entity)
}

const RecipientToDepotStepKey = "recipient_to_depot"
export type RecipientToDepotStepKey = typeof RecipientToDepotStepKey

export const recipientToDepotStep: Step<
  RecipientToDepotStepKey,
  RecipientToDepotFormProps
> = {
  key: RecipientToDepotStepKey,
  title: i18next.t("Redevable et dépôt destinataire"),
  allowNextStep: showNextStepRecipientToDepotForm,
}
