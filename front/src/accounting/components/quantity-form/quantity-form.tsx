import { Balance, CreateOperationType } from "accounting/types"
import { useFormContext } from "common/components/form2"
import { Trans, useTranslation } from "react-i18next"
import { NumberInput } from "common/components/inputs2"
import { Button } from "common/components/button2"
import { Notice } from "common/components/notice"
import { useRef, useState } from "react"
import { useUnit } from "common/hooks/unit"
import { QuantityFormProps } from "./quantity-form.types"
import { getQuantityInputLabel } from "./quantity-form.utils"
import { useQuantityForm } from "./quantity-form.hooks"
import { ExtendedUnit, Unit } from "common/types"

export type QuantityFormComponentProps = {
  balance: Balance

  // Maximum quantity allowed
  quantityMax?: number

  type: CreateOperationType

  // Unit of the quantity displayed to the user (default is the entity preferred unit)
  unit?: Unit | ExtendedUnit

  // Unit of the quantity used by the backend (default is the entity preferred unit)
  backendUnit?: Unit | ExtendedUnit

  // Custom conversion function for the backend (default is the value passed as parameter)
  converter?: (value: number) => number

  // Lot GHG min and max bounds
  gesBoundMin?: number
  gesBoundMax?: number

  // Callback function to be called when the quantity is valid and overrides the default behavior
  onQuantityDeclared?: (emissions: {
    emissionsMin: number
    emissionsMax: number
  }) => void
}

const formatEmissionMin = (value: number) => Math.ceil(value * 10) / 10
export const formatEmissionMax = (value: number) => Math.floor(value * 10) / 10

const AvoidedEmissionsSection = () => {
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
      {...bind("avoided_emissions")}
      required
    />
  )
}

const QuantitySection = ({
  balance,
  quantityMax,
  type,
  unit: customUnit,
  backendUnit: customBackendUnit,
  gesBoundMin,
  gesBoundMax,
  converter,
  onQuantityDeclared,
}: QuantityFormComponentProps) => {
  const { t } = useTranslation()
  const { formatUnit, unit } = useUnit(customUnit)
  const quantityInputRef = useRef<HTMLInputElement>(null)

  const { value, bind, setField, setFieldError } =
    useFormContext<QuantityFormProps>()
  const mutation = useQuantityForm({
    balance,
    values: value,
    unit: customBackendUnit,
    converter,
    gesBoundMin,
    gesBoundMax,
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
          { max: formatUnit(quantityMax, { fractionDigits: 0 }) }
        )
      )
      return
    }

    mutation.execute().then((response) => {
      const emissions = response.data
      const emissionsMin = emissions?.min_avoided_emissions
        ? Math.trunc(emissions.min_avoided_emissions)
        : 0
      const emissionsMax = emissions?.max_avoided_emissions
        ? Math.trunc(emissions?.max_avoided_emissions)
        : 0

      if (emissionsMin === 0) {
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

      if (onQuantityDeclared) {
        onQuantityDeclared({
          emissionsMin,
          emissionsMax,
        })
      } else {
        setField("avoided_emissions_min", emissionsMin)
        setField("avoided_emissions_max", emissionsMax)

        if (emissionsMin === emissionsMax) {
          setField("avoided_emissions", emissionsMin)
        }
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

  return (
    <>
      <NumberInput
        label={`${getQuantityInputLabel(type)} (${unit.toLocaleUpperCase()})`}
        step={1}
        max={quantityMax}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            declareQuantity()
          }
        }}
        {...quantityBind}
        addon={
          <>
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
        stateRelatedMessage={
          quantityBind.state === "error"
            ? quantityBind.stateRelatedMessage
            : t(
                "Le nombre de tonnes de CO2 évitées équivalentes sera calculé après validation de la quantité."
              )
        }
        state={
          quantityBind.state === "error"
            ? "error"
            : quantityDeclared
              ? "default"
              : "info"
        }
        disabled={quantityDeclared || mutation.loading}
        required
        inputRef={quantityInputRef}
      />
      {quantityDeclared &&
      value.avoided_emissions_min &&
      value.avoided_emissions_max &&
      value.avoided_emissions_min > 0 &&
      value.avoided_emissions_max > 0 ? (
        <Notice noColor variant="info">
          {value.avoided_emissions_min === value.avoided_emissions_max ? (
            <Trans
              components={{ strong: <strong /> }}
              t={t}
              values={{
                quantity: formatUnit(value.quantity!, {
                  fractionDigits: 10,
                }),
                value: value.avoided_emissions_min,
              }}
              defaults="Pour une quantité de <strong>{{quantity}}</strong>, vous pouvez enregistrer <strong>{{value}} tCO2 évitées</strong>."
            />
          ) : (
            <Trans
              components={{ strong: <strong /> }}
              t={t}
              values={{
                quantity: formatUnit(value.quantity!, {
                  fractionDigits: 10,
                }),
                min: value.avoided_emissions_min,
                max: value.avoided_emissions_max,
              }}
              defaults="Pour une quantité de <strong>{{quantity}}</strong>, vous pouvez enregistrer entre <strong>{{min}} et {{max}} tCO2 évitées</strong>."
            />
          )}
        </Notice>
      ) : null}
    </>
  )
}

export const QuantityForm = (props: QuantityFormComponentProps) => {
  return (
    <>
      <QuantitySection {...props} />
      <AvoidedEmissionsSection />
    </>
  )
}

QuantityForm.Quantity = QuantitySection
QuantityForm.AvoidedEmissions = AvoidedEmissionsSection
