import { Balance } from "accounting/types"
import { useFormContext } from "common/components/form2"
import { Trans, useTranslation } from "react-i18next"
import { NumberInput } from "common/components/inputs2"
import { Button } from "common/components/button2"
import { Notice } from "common/components/notice"
import { useState } from "react"
import { useUnit } from "common/hooks/unit"
import {
  formatEmissionMax,
  QuantityFormProps,
  QuantitySummary as ExportationQuantitySummary,
  quantityFormStep,
  quantityFormStepKey as exportationQuantityFormStepKey,
} from "accounting/components/quantity-form"
import { useQuantityForm } from "accounting/components/quantity-form/quantity-form.hooks"

export type ExportationQuantityFormProps = Pick<
  QuantityFormProps,
  "quantity" | "avoided_emissions"
>

type ExportationQuantityFormComponentProps = {
  balance: Balance
  depot_quantity_max?: number
}

export const ExportationQuantityForm = ({
  balance,
  depot_quantity_max,
}: ExportationQuantityFormComponentProps) => {
  const { t } = useTranslation()
  const { formatUnit } = useUnit()
  const { value, bind, setField } =
    useFormContext<ExportationQuantityFormProps>()
  const mutation = useQuantityForm({ balance, values: value })
  const [quantityDeclared, setQuantityDeclared] = useState(
    value.avoided_emissions !== undefined
  )

  const declareQuantity = () => {
    mutation.execute().then((response) => {
      const emissions = response.data
      setField(
        "avoided_emissions",
        formatEmissionMax(emissions?.max_avoided_emissions ?? 0)
      )
      setQuantityDeclared(true)
    })
  }

  const resetQuantityDeclared = () => {
    setField("avoided_emissions", undefined)
    setQuantityDeclared(false)
  }

  return (
    <>
      <NumberInput
        label={t("Saisir une quantité pour l'exportation")}
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
        disabled={quantityDeclared || mutation.loading}
        required
      />
      {quantityDeclared && value.avoided_emissions && (
        <Notice noColor variant="info">
          <Trans
            components={{ strong: <strong /> }}
            t={t}
            values={{
              quantity: formatUnit(value.quantity!, 0),
              avoided_emissions: formatEmissionMax(value.avoided_emissions),
            }}
            defaults="{{quantity}} : <strong>{{avoided_emissions}} tonnes de CO2 équivalent évitées</strong>"
          />
        </Notice>
      )}
    </>
  )
}

export const exportationQuantityFormStep = (
  values: ExportationQuantityFormProps
) => {
  return {
    ...quantityFormStep(values),
    allowNextStep: Boolean(
      values.quantity &&
        values.quantity > 0 &&
        values.avoided_emissions &&
        values.avoided_emissions > 0
    ),
  }
}
export { ExportationQuantitySummary, exportationQuantityFormStepKey }
