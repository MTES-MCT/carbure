import i18next, { TFunction } from "i18next"
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
  values: QuantityFormProps,
  overrides?: Partial<Step<QuantityFormStepKey>>
) => Step<QuantityFormStepKey> = (values, overrides) => {
  return {
    key: quantityFormStepKey,
    title: i18next.t(
      "Quantité d'énergie consommée et tonnes de CO2 évitées équivalentes"
    ),
    allowNextStep: showNextStepQuantityForm(values),
    ...overrides,
  }
}

export const getQuantityInputLabel = (type: CreateOperationType) => {
  switch (type) {
    case CreateOperationType.CESSION:
      return i18next.t("Saisir une quantité d'énergie à céder")
    case CreateOperationType.EXPORTATION:
      return i18next.t("Saisir une quantité pour l'exportation")
    case CreateOperationType.TENEUR:
      return i18next.t("Saisir une quantité d'énergie consommée")
    case CreateOperationType.TRANSFERT:
      return i18next.t("Saisir une quantité d'énergie à transférer")
    default:
      return i18next.t("Type inconnu")
  }
}

type QuantityInputFeedback = {
  state: "default" | "info"
  stateRelatedMessage?: string
}

export const getQuantityInputFeedback = ({
  type,
  quantityDeclared,
  t,
}: {
  type: CreateOperationType
  quantityDeclared: boolean
  t: TFunction
}): QuantityInputFeedback => {
  if (!quantityDeclared && type === CreateOperationType.TENEUR) {
    return {
      state: "info",
      stateRelatedMessage: t(
        "L'équivalent en GJ est affiché dès que vous entrez une quantité."
      ),
    }
  }

  return {
    state: "info",
    stateRelatedMessage: t(
      "Le nombre de tonnes de CO2 évitées équivalentes sera calculé après validation de la quantité."
    ),
  }
}

export const showEnergyEquivalent = (
  type: CreateOperationType,
  quantity?: number,
  pciLitre?: number
) => type === CreateOperationType.TENEUR && Boolean(quantity && pciLitre)
