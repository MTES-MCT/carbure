import { Autocomplete } from "common/components/autocomplete2"
import { useFormContext } from "common/components/form2"
import { SessionDialogForm } from "../cession-dialog.types"
import { findBiofuelEntities, findDepots } from "carbure/api"
import {
  normalizeDepot,
  normalizeEntityPreview,
} from "carbure/utils/normalizers"
import { useTranslation } from "react-i18next"

export const showNextStepRecipientToDepotForm = (values: SessionDialogForm) => {
  return values.credited_entity
}

export const RecipientToDepotForm = () => {
  const { t } = useTranslation()
  const { bind } = useFormContext<SessionDialogForm>()

  return (
    <>
      <Autocomplete
        label={t("Sélectionner un redevable")}
        getOptions={findBiofuelEntities}
        normalize={normalizeEntityPreview}
        {...bind("credited_entity")}
        required
      />
      <Autocomplete
        label={t("Sélectionner un dépôt")}
        getOptions={findDepots}
        normalize={normalizeDepot}
        {...bind("to_depot")}
      />
    </>
  )
}
