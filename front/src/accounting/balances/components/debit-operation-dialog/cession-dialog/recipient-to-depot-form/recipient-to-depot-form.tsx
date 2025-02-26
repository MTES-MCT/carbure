import { Autocomplete } from "common/components/autocomplete2"
import { useFormContext } from "common/components/form2"
import { SessionDialogForm } from "../cession-dialog.types"
import { findBiofuelEntities, findDepots } from "carbure/api"
import {
  normalizeDepot,
  normalizeEntityPreview,
} from "carbure/utils/normalizers"
import { useTranslation } from "react-i18next"
import { Grid } from "common/components/scaffold"
import { OperationText } from "accounting/components/operation-text"

export const showNextStepRecipientToDepotForm = (values: SessionDialogForm) => {
  return values.credited_entity
}

export const RecipientToDepotForm = () => {
  const { t } = useTranslation()
  const { bind } = useFormContext<SessionDialogForm>()

  return (
    <>
      <Autocomplete
        label={t("Rechercher un redevable")}
        getOptions={findBiofuelEntities}
        normalize={normalizeEntityPreview}
        {...bind("credited_entity")}
        required
      />
      <Autocomplete
        label={t("Rechercher un dépôt")}
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
  values: SessionDialogForm
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
