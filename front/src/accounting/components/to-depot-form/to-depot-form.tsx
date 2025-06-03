import { findDepots } from "common/api"
import { Autocomplete } from "common/components/autocomplete2"
import { useFormContext } from "common/components/form2"
import { Depot } from "common/types"
import { normalizeDepot } from "common/utils/normalizers"
import { useTranslation } from "react-i18next"
import { OperationText } from "../operation-text"

export type ToDepotFormProps = {
  to_depot?: Depot
}

export const ToDepotForm = () => {
  const { t } = useTranslation()
  const { bind } = useFormContext<ToDepotFormProps>()

  return (
    <Autocomplete
      label={t("Sélectionnez un dépôt destinataire")}
      placeholder={t("Rechercher un dépôt")}
      getOptions={findDepots}
      normalize={normalizeDepot}
      {...bind("to_depot")}
    />
  )
}

export const ToDepotSummary = ({ values }: { values: ToDepotFormProps }) => {
  const { t } = useTranslation()

  if (!values.to_depot) {
    return null
  }

  return (
    <OperationText
      title={t("Dépôt destinataire")}
      description={values.to_depot?.name ?? ""}
    />
  )
}
