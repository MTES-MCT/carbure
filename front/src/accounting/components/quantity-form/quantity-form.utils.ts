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

export const quantityFormStepKey = "quantity-form"
type QuantityFormStepKey = typeof quantityFormStepKey

export const quantityFormStep: (
  values: QuantityFormProps
) => Step<QuantityFormStepKey> = (values) => ({
  key: quantityFormStepKey,
  title: i18next.t("Quantité de la cession et tCO2 évitées"),
  allowNextStep: showNextStepQuantityForm(values),
})
