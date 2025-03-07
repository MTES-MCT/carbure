import { Balance } from "accounting/pages/balances/types"
import { useFormContext } from "common/components/form2"
import { Trans, useTranslation } from "react-i18next"
import { NumberInput } from "common/components/inputs2"
import { Button } from "common/components/button2"
import { simulateMinMax } from "accounting/api"
import useEntity from "carbure/hooks/entity"
import { useMutation } from "common/hooks/async"
import { Notice } from "common/components/notice"
import { useState } from "react"
import { Grid } from "common/components/scaffold"
import { OperationText } from "accounting/components/operation-text"
import { useUnit } from "common/hooks/unit"

export type QuantityFormProps = {
  quantity?: number
  avoided_emissions_min?: number // Range determined by the simulation
  avoided_emissions_max?: number // Range determined by the simulation
  avoided_emissions?: number // Value selected by the user
}

type QuantityFormComponentProps = {
  balance: Balance
  depot_quantity_max?: number
}

export const showNextStepQuantityForm = (values: QuantityFormProps) => {
  return (
    values.quantity &&
    values.quantity > 0 &&
    values.avoided_emissions &&
    values.avoided_emissions_min &&
    values.avoided_emissions_max &&
    values.avoided_emissions >= values.avoided_emissions_min &&
    values.avoided_emissions <= values.avoided_emissions_max
  )
}

const formatEmissionMin = (value: number) => Math.ceil(value * 10) / 10
const formatEmissionMax = (value: number) => Math.floor(value * 10) / 10

export const QuantityForm = ({
  balance,
  depot_quantity_max,
}: QuantityFormComponentProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { formatUnit, unit } = useUnit()
  const { value, bind, setField } = useFormContext<QuantityFormProps>()
  const mutation = useMutation(simulateMinMax)
  const [quantityDeclared, setQuantityDeclared] = useState(
    value.avoided_emissions_min !== undefined &&
      value.avoided_emissions_max !== undefined
  )

  const declareQuantity = () => {
    mutation
      .execute(entity.id, {
        biofuel: balance.biofuel?.id ?? null,
        customs_category: balance.customs_category,
        debited_entity: entity.id,
        target_volume: value.quantity!,
        target_emission: 0,
        unit: entity.preferred_unit,
      })
      .then((response) => {
        const emissions = response.data
        setField("avoided_emissions_min", emissions?.min_avoided_emissions)
        setField("avoided_emissions_max", emissions?.max_avoided_emissions)
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
        label={`${t("Saisir une quantité pour la cession")} (${unit})`}
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
              <Trans
                components={{ strong: <strong /> }}
                t={t}
                values={{
                  quantity: formatUnit(value.quantity!, 0),
                  min: formatEmissionMin(value.avoided_emissions_min),
                  max: formatEmissionMax(value.avoided_emissions_max),
                }}
                defaults="Pour une quantité de <strong>{{quantity}}</strong>, vous pouvez enregistrer entre <strong>{{min}} et {{max}} tC02 évitées</strong>."
              />
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
    <Grid>
      <OperationText
        title={t("Quantité de la cession")}
        description={formatUnit(values.quantity, 0)}
      />
      <OperationText
        title={t("TCO2 évitées équivalentes")}
        description={values.avoided_emissions}
      />
    </Grid>
  )
}
