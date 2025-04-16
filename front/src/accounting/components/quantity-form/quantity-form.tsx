import { Balance, CreateOperationType } from "accounting/types"
import { useFormContext } from "common/components/form2"
import { Trans, useTranslation } from "react-i18next"
import { NumberInput } from "common/components/inputs2"
import { Button } from "common/components/button2"
import { Notice } from "common/components/notice"
import { useState } from "react"
import { OperationText } from "accounting/components/operation-text"
import { useUnit } from "common/hooks/unit"
import { QuantityFormProps } from "./quantity-form.types"
import { getQuantityInputLabel } from "./quantity-form.utils"
import { useQuantityForm } from "./quantity-form.hooks"
import { ExtendedUnit, Unit } from "common/types"
import { formatNumber } from "common/utils/formatters"

type QuantityFormComponentProps = {
  balance: Balance
  depot_quantity_max?: number
  type: CreateOperationType

  // Unit of the quantity displayed to the user (default is the entity preferred unit)
  unit?: Unit | ExtendedUnit

  // Unit of the quantity used by the backend (default is the entity preferred unit)
  backendUnit?: Unit | ExtendedUnit

  // Custom conversion function for the backend (default is the value passed as parameter)
  converter?: (value: number) => number

  // Depot id can be used to known in which depot the quantity will be picked up
  depotId?: number
}

const formatEmissionMin = (value: number) => Math.ceil(value * 10) / 10
export const formatEmissionMax = (value: number) => Math.floor(value * 10) / 10

export const QuantityForm = ({
  balance,
  depot_quantity_max,
  type,
  unit: customUnit,
  backendUnit: customBackendUnit,
  depotId,
  converter,
}: QuantityFormComponentProps) => {
  const { t } = useTranslation()
  const { formatUnit, unit } = useUnit(customUnit)

  const { value, bind, setField, setFieldError } =
    useFormContext<QuantityFormProps>()
  const mutation = useQuantityForm({
    balance,
    values: value,
    unit: customBackendUnit,
    converter,
    depotId,
  })
  const [quantityDeclared, setQuantityDeclared] = useState(
    value.avoided_emissions_min !== undefined &&
      value.avoided_emissions_max !== undefined
  )

  const declareQuantity = () => {
    if (!value.quantity) return

    if (depot_quantity_max && value.quantity > depot_quantity_max) {
      setFieldError(
        "quantity",
        t(
          "La quantité déclarée est supérieure à la quantité maximale autorisée. Merci de modifier la quantité."
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
      setField("avoided_emissions_min", emissionsMin)
      setField("avoided_emissions_max", emissionsMax)

      if (emissionsMin === emissionsMax) {
        setField("avoided_emissions", emissionsMin)
      }
      setQuantityDeclared(true)
    })
  }

  const resetQuantityDeclared = () => {
    setField("avoided_emissions_min", undefined)
    setField("avoided_emissions_max", undefined)
    setQuantityDeclared(false)
  }

  return (
    <>
      <NumberInput
        label={`${getQuantityInputLabel(type)} (${unit.toLocaleUpperCase()})`}
        step={1}
        max={depot_quantity_max}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            declareQuantity()
          }
        }}
        {...bind("quantity")}
        addon={
          <>
            {!quantityDeclared && (
              <Button
                onClick={declareQuantity}
                loading={mutation.loading}
                disabled={
                  !value.quantity ||
                  value.quantity === 0 ||
                  (depot_quantity_max !== undefined &&
                    value.quantity > depot_quantity_max)
                }
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
        stateRelatedMessage={t(
          "Nous pourrons ensuite vous indiquer les tCO2 évitées équivalentes pour cette quantité."
        )}
        state={quantityDeclared ? "default" : "info"}
        disabled={quantityDeclared || mutation.loading}
        required
      />
      {quantityDeclared &&
      value.avoided_emissions_min &&
      value.avoided_emissions_max &&
      value.avoided_emissions_min > 0 &&
      value.avoided_emissions_max > 0 ? (
        <>
          <Notice noColor variant="info">
            {value.avoided_emissions_min === value.avoided_emissions_max ? (
              <Trans
                components={{ strong: <strong /> }}
                t={t}
                values={{
                  quantity: formatUnit(value.quantity!, {
                    fractionDigits: 10,
                    appendZeros: false,
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
                    appendZeros: false,
                  }),
                  min: value.avoided_emissions_min,
                  max: value.avoided_emissions_max,
                }}
                defaults="Pour une quantité de <strong>{{quantity}}</strong>, vous pouvez enregistrer entre <strong>{{min}} et {{max}} tCO2 évitées</strong>."
              />
            )}
          </Notice>
          <NumberInput
            label={t("Saisir un montant en tCO2 évitées")}
            min={formatEmissionMin(value.avoided_emissions_min)}
            max={formatEmissionMax(value.avoided_emissions_max)}
            {...bind("avoided_emissions")}
            required
          />
        </>
      ) : null}
      {quantityDeclared && value.avoided_emissions_min === 0 && (
        <Notice noColor variant="warning">
          {t(
            "La quantité entrée n'est pas suffisante pour enregistrer des tCO2 évitées. Merci de modifier la quantité."
          )}
        </Notice>
      )}
    </>
  )
}

export const QuantitySummary = ({
  values,
  unit,
}: {
  values: QuantityFormProps
  unit?: Unit | ExtendedUnit
}) => {
  const { t } = useTranslation()
  const { formatUnit } = useUnit(unit)
  if (!values.quantity || !values.avoided_emissions) {
    return null
  }

  return (
    <>
      <OperationText
        title={t("Quantité")}
        description={formatUnit(values.quantity, {
          fractionDigits: 10,
          appendZeros: false,
        })}
      />
      <OperationText
        title={t("TCO2 évitées équivalentes")}
        description={formatNumber(values.avoided_emissions, {
          fractionDigits: 10,
          appendZeros: false,
        })}
      />
    </>
  )
}
