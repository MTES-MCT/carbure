import { Step } from "common/components/stepper"
import { FromDepotFormProps } from "./from-depot-form.types"
import i18next from "i18next"

export const showNextStepFromDepotForm = (values: FromDepotFormProps) => {
  return Boolean(
    values.from_depot?.available_balance &&
      values.from_depot.available_balance > 0
  )
}

export const fromDepotStepKey = "from-depot"
type FromDepotStepKey = typeof fromDepotStepKey

export const fromDepotStep: (
  values: FromDepotFormProps
) => Step<FromDepotStepKey> = (values) => ({
  key: fromDepotStepKey,
  title: i18next.t("Dépôt d'expédition"),
  allowNextStep: showNextStepFromDepotForm(values),
})
