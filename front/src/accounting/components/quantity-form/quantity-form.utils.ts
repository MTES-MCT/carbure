import i18next from "i18next"
import { QuantityFormProps } from "./quantity-form.types"
import { Step } from "common/components/stepper"
import { CreateOperationType } from "accounting/types"

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
) => Step<QuantityFormStepKey> = (values) => {
  return {
    key: quantityFormStepKey,
    title: i18next.t("Quantité"),
    allowNextStep: showNextStepQuantityForm(values),
  }
}

export const getQuantityInputLabel = (type: CreateOperationType) => {
  switch (type) {
    case CreateOperationType.CESSION:
      return i18next.t("Saisir une quantité pour la cession")
    case CreateOperationType.EXPORTATION:
      return i18next.t("Saisir une quantité pour l'exportation")
    case CreateOperationType.TENEUR:
      return i18next.t("Saisir une quantité pour la teneur")
    default:
      return i18next.t("Type inconnu")
  }
}

export const getQuantitySummaryTitle = (type: CreateOperationType) => {
  switch (type) {
    case CreateOperationType.CESSION:
      return i18next.t("Quantité de la cession")
    case CreateOperationType.EXPORTATION:
      return i18next.t("Quantité de l'exportation")
    case CreateOperationType.TENEUR:
      return i18next.t("Quantité de la teneur")
    default:
      return i18next.t("Type inconnu")
  }
}
