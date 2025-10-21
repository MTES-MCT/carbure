import { useFormContext } from "common/components/form2"
import { Autocomplete } from "common/components/autocomplete2"
import { useTranslation } from "react-i18next"
import useEntity from "common/hooks/entity"
import { OperationText } from "accounting/components/operation-text"
import { useQuery } from "common/hooks/async"
import { FromDepotFormProps } from "./from-depot-form.types"
import { getDeliverySites } from "common/api"

export const FromDepotForm = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { bind } = useFormContext<FromDepotFormProps>()

  const entityDepots = useQuery(() => getDeliverySites(entity.id), {
    key: "cession-depots",
    params: [],
  })

  return (
    <Autocomplete
      label={t("Sélectionnez un dépôt d'expédition")}
      placeholder={t("Rechercher un dépôt")}
      options={entityDepots.result?.data ?? []}
      normalize={(entityDepot) => ({
        value: entityDepot.depot!,
        label: entityDepot.depot!.name,
      })}
      {...bind("from_depot")}
      required
    />
  )
}

// Recap form data after the step was submitted
export const FromDepotSummary = ({
  values,
}: {
  values: FromDepotFormProps
}) => {
  const { t } = useTranslation()

  if (!values.from_depot) {
    return null
  }

  return (
    <OperationText
      title={t("Dépôt d'expédition")}
      description={values.from_depot?.name ?? ""}
    />
  )
}
