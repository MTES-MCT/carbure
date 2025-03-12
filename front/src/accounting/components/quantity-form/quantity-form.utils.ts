import i18next from "i18next"
import { QuantityFormProps } from "./quantity-form.types"
import { Step } from "common/components/stepper"

const showNextStepQuantityForm = (values: QuantityFormProps) => {
  return Boolean(
    values.quantity &&
      values.quantity > 0 &&
      values.avoided_emissions &&
      values.avoided_emissions_min &&
      values.avoided_emissions_max &&
      values.avoided_emissions >= values.avoided_emissions_min &&
      values.avoided_emissions <= values.avoided_emissions_max
  )
}

const quantityFormStepKey = "quantity-form"
export type QuantityFormStepKey = typeof quantityFormStepKey

export const quantityFormStep: Step<QuantityFormStepKey, QuantityFormProps> = {
  key: quantityFormStepKey,
  title: i18next.t("Quantité de la cession et tCO2 évitées"),
  allowNextStep: showNextStepQuantityForm,
}
