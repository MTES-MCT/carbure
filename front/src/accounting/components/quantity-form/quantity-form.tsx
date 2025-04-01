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

type QuantityFormComponentProps = {
  balance: Balance
  depot_quantity_max?: number
  type: CreateOperationType
}

const formatEmissionMin = (value: number) => Math.ceil(value * 10) / 10
export const formatEmissionMax = (value: number) => Math.floor(value * 10) / 10

export const QuantityForm = ({
  balance,
  depot_quantity_max,
  type,
}: QuantityFormComponentProps) => {
  const { t } = useTranslation()
  const { formatUnit, unit } = useUnit()
  const { value, bind, setField } = useFormContext<QuantityFormProps>()
  const mutation = useQuantityForm({ balance, values: value })
  const [quantityDeclared, setQuantityDeclared] = useState(
    value.avoided_emissions_min !== undefined &&
      value.avoided_emissions_max !== undefined
  )

  const declareQuantity = () => {
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
        max={depot_quantity_max}
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
                {t("Déclarer la quantité")}
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
          "Nous pourrons ensuite vous indiquer les tC02 évitées équivalentes pour cette quantité."
        )}
        state={quantityDeclared ? "default" : "info"}
        disabled={quantityDeclared || mutation.loading}
        required
      />
      {quantityDeclared &&
        value.avoided_emissions_min &&
        value.avoided_emissions_max && (
          <>
            <Notice noColor variant="info">
              {value.avoided_emissions_min === value.avoided_emissions_max ? (
                <Trans
                  components={{ strong: <strong /> }}
                  t={t}
                  values={{
                    quantity: formatUnit(value.quantity!, 0),
                    value: value.avoided_emissions_min,
                  }}
                  defaults="Pour une quantité de <strong>{{quantity}}</strong>, vous pouvez enregistrer <strong>{{value}} tC02 évitées</strong>."
                />
              ) : (
                <Trans
                  components={{ strong: <strong /> }}
                  t={t}
                  values={{
                    quantity: formatUnit(value.quantity!, 0),
                    min: value.avoided_emissions_min,
                    max: value.avoided_emissions_max,
                  }}
                  defaults="Pour une quantité de <strong>{{quantity}}</strong>, vous pouvez enregistrer entre <strong>{{min}} et {{max}} tC02 évitées</strong>."
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
        )}
    </>
  )
}

export const QuantitySummary = ({ values }: { values: QuantityFormProps }) => {
  const { t } = useTranslation()
  const { formatUnit } = useUnit()
  if (!values.quantity || !values.avoided_emissions) {
    return null
  }

  return (
    <>
      <OperationText
        title={t("Quantité")}
        description={formatUnit(values.quantity, 0)}
      />
      <OperationText
        title={t("TCO2 évitées équivalentes")}
        description={values.avoided_emissions}
      />
    </>
  )
}
