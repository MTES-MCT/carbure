import { Balance, CreateOperationType } from "accounting/types"
import { useFormContext } from "common/components/form2"
import { useTranslation } from "react-i18next"
import { NumberInput } from "common/components/inputs2"
import { Button } from "common/components/button2"
import { useEffect, useRef, useState } from "react"
import { useUnit } from "common/hooks/unit"
import { QuantityFormProps } from "./quantity-form.types"
import {
  formatAvoidedEmissionsBounds,
  formatEmissionMax,
  formatEmissionMin,
  getQuantityInputFeedback,
  getQuantityInputLabel,
  showEnergyEquivalent,
} from "./quantity-form.utils"
import {
  useFocusOnAvoidedEmissions,
  useQuantityForm,
} from "./quantity-form.hooks"
import { AdvancedFiltersFormProps } from "../advanced-filters/advanced-filters.types"
import { formatAccountingUnit } from "accounting/utils/formatters"
import {
  DEFAULT_UNIT_OPERATION,
  FRACTION_DIGITS_LITERS,
  FRACTION_DIGITS_TCO2,
} from "accounting/config"
import { EnergyEquivalentNotice } from "./quantity-form-energy-equivalent"
import { AvoidedEmissionsRecapNotice } from "./quantity-form-avoided-emissions-notice"
import { getStepFromFractionDigits } from "common/utils/formatters"

export type QuantityFormComponentProps = {
  balance: Balance

  // Maximum quantity allowed
  quantityMax: number

  type: CreateOperationType

  // Lot GHG min and max bounds
  gesBoundMin?: number
  gesBoundMax?: number

  // Callback function to be called when the quantity is declared
  onQuantityDeclared?: () => void
}

const AvoidedEmissionsSection = ({
  inputRef,
}: {
  inputRef?: React.RefObject<HTMLInputElement>
}) => {
  const { value, bind } = useFormContext<QuantityFormProps>()
  const { t } = useTranslation()

  if (!value.avoided_emissions_min || !value.avoided_emissions_max) {
    return null
  }

  return (
    <NumberInput
      label={t("Saisir un montant en tCO2 évitées")}
      min={formatEmissionMin(value.avoided_emissions_min)}
      max={formatEmissionMax(value.avoided_emissions_max)}
      step={getStepFromFractionDigits(FRACTION_DIGITS_TCO2)}
      {...bind("avoided_emissions")}
      required
      inputRef={inputRef}
    />
  )
}

const QuantitySection = ({
  balance,
  quantityMax,
  type,
  onQuantityDeclared,
}: QuantityFormComponentProps) => {
  const { t } = useTranslation()
  const { unit } = useUnit(DEFAULT_UNIT_OPERATION)
  const quantityInputRef = useRef<HTMLInputElement>(null)

  const { value, bind, setField, setFieldError } = useFormContext<
    QuantityFormProps & AdvancedFiltersFormProps
  >()
  const mutation = useQuantityForm({
    balance,
  })
  const [quantityDeclared, setQuantityDeclared] = useState(
    value.avoided_emissions_min !== undefined &&
      value.avoided_emissions_max !== undefined
  )

  const declareQuantity = () => {
    if (!value.quantity) return

    if (quantityMax && value.quantity > quantityMax) {
      setFieldError(
        "quantity",
        t(
          "La quantité déclarée est supérieure à la quantité maximale autorisée ({{max}}). Merci de modifier la quantité.",
          {
            max: formatAccountingUnit(quantityMax, unit),
          }
        )
      )
      return
    }

    mutation.execute().then((response) => {
      const emissions = response.data

      if (
        !emissions?.min_avoided_emissions ||
        !emissions?.max_avoided_emissions
      ) {
        return
      }

      const {
        min: emissionsMin,
        max: emissionsMax,
        isInsufficient,
      } = formatAvoidedEmissionsBounds(
        emissions.min_avoided_emissions,
        emissions.max_avoided_emissions
      )

      // User can only enter avoided emissions if the emission min returned by the API is greater than 1 tCO2
      if (isInsufficient) {
        quantityInputRef.current?.setCustomValidity(
          t(
            "La quantité entrée n'est pas suffisante pour enregistrer des tCO2 évitées. Merci de modifier la quantité."
          )
        )
        requestAnimationFrame(() => {
          quantityInputRef.current?.reportValidity()
        })
        return
      }

      setQuantityDeclared(true)
      setField("avoided_emissions_min", emissionsMin)
      setField("avoided_emissions_max", emissionsMax)

      onQuantityDeclared?.()

      if (emissionsMin === emissionsMax) {
        setField("avoided_emissions", emissionsMin)
      }
    })
  }

  const resetQuantityDeclared = () => {
    setField("avoided_emissions_min", undefined)
    setField("avoided_emissions_max", undefined)
    setQuantityDeclared(false)
  }

  const quantityBind = bind("quantity", {
    showError: true,
    onChange: () => {
      // Reset the custom validity of the quantity input when the quantity is changed
      quantityInputRef.current?.setCustomValidity("")
      quantityInputRef.current?.reportValidity()
    },
  })

  const quantityMaxLabel = value.availableBalance
    ? `(${t("solde")}: ${formatAccountingUnit(value.availableBalance, unit)})`
    : undefined

  const { state: hintState, stateRelatedMessage: hintMessage } =
    getQuantityInputFeedback({
      quantityDeclared,
      t,
    })

  const isError = quantityBind.state === "error"
  const state = isError ? "error" : hintState
  const stateRelatedMessage = isError
    ? quantityBind.stateRelatedMessage
    : hintMessage

  const pciLitre = balance.biofuel?.pci_litre

  // When the component is mounted, reset the quantity declared if the quantity is greater than the quantity max
  useEffect(() => {
    if (quantityMax && value.quantity && value.quantity > quantityMax) {
      resetQuantityDeclared()
      setField("quantity", undefined)
    }
  }, [])

  return (
    <>
      <NumberInput
        label={`${getQuantityInputLabel(type)} ${quantityMaxLabel ?? ""}`}
        step={getStepFromFractionDigits(FRACTION_DIGITS_LITERS)}
        min={0}
        max={quantityMax}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            declareQuantity()
          }
        }}
        {...quantityBind}
        addon={
          <>
            <Button
              priority="secondary"
              onClick={() => quantityBind.onChange(quantityMax)}
              disabled={quantityDeclared}
            >
              {t("Max")}
            </Button>
            {!quantityDeclared && (
              <Button
                onClick={declareQuantity}
                loading={mutation.loading}
                disabled={!value.quantity || value.quantity === 0}
              >
                {t("Valider la quantité")}
              </Button>
            )}
            {quantityDeclared && (
              <Button priority="secondary" onClick={resetQuantityDeclared}>
                {t("Modifier")}
              </Button>
            )}
          </>
        }
        state={state}
        stateRelatedMessage={stateRelatedMessage}
        disabled={quantityDeclared || mutation.loading}
        required
        inputRef={quantityInputRef}
      />
      {showEnergyEquivalent(type, value.quantity, pciLitre) && (
        <EnergyEquivalentNotice
          quantityLiters={value.quantity!}
          pciLitre={pciLitre!}
        />
      )}
      {quantityDeclared && (
        <AvoidedEmissionsRecapNotice
          quantity={value.quantity}
          avoided_emissions_min={value.avoided_emissions_min}
          avoided_emissions_max={value.avoided_emissions_max}
        />
      )}
    </>
  )
}

export const QuantityForm = (props: QuantityFormComponentProps) => {
  const { avoidedEmissionsInputRef, handleQuantityDeclared } =
    useFocusOnAvoidedEmissions()

  return (
    <>
      <QuantitySection {...props} onQuantityDeclared={handleQuantityDeclared} />
      <AvoidedEmissionsSection inputRef={avoidedEmissionsInputRef} />
    </>
  )
}

QuantityForm.Quantity = QuantitySection
QuantityForm.AvoidedEmissions = AvoidedEmissionsSection
