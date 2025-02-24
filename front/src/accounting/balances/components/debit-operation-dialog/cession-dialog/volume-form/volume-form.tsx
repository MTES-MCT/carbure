import { Balance } from "accounting/balances/types"
import { useFormContext } from "common/components/form2"
import { Trans, useTranslation } from "react-i18next"
import { SessionDialogForm } from "../cession-dialog.types"
import { NumberInput } from "common/components/inputs2"
import { Button } from "common/components/button2"
import { simulateMinMax } from "accounting/api"
import useEntity from "carbure/hooks/entity"
import { useMutation } from "common/hooks/async"
import { Notice } from "common/components/notice"
import { useState } from "react"
import { formatNumber, roundNumber } from "common/utils/formatters"

type VolumeFormProps = {
  balance: Balance
}

export const showNextStepVolumeForm = (values: SessionDialogForm) => {
  return (
    values.volume &&
    values.volume > 0 &&
    values.avoided_emissions &&
    values.avoided_emissions_min &&
    values.avoided_emissions_max &&
    values.avoided_emissions >= values.avoided_emissions_min &&
    values.avoided_emissions <= values.avoided_emissions_max
  )
}

export const VolumeForm = ({ balance }: VolumeFormProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { value, bind, setField } = useFormContext<SessionDialogForm>()
  const mutation = useMutation(simulateMinMax)
  const [volumeDeclared, setVolumeDeclared] = useState(false)

  const declareQuantity = () => {
    mutation
      .execute(entity.id, {
        biofuel: 33,
        customs_category: balance.customs_category,
        debited_entity: entity.id,
        target_volume: value.volume!,
        target_emission: 0,
      })
      .then((response) => {
        const emissions = response.data
        // @ts-ignore fixed soon by the backend
        setField("avoided_emissions_min", emissions.min_avoided_emissions)
        // @ts-ignore fixed soon by the backend
        setField("avoided_emissions_max", emissions.max_avoided_emissions)
        setVolumeDeclared(true)
      })
  }
  return (
    <>
      <NumberInput
        label={t("Saisir une quantité pour la cession")}
        {...bind("volume")}
        addon={
          <>
            {!volumeDeclared && (
              <Button onClick={declareQuantity} loading={mutation.loading}>
                {t("Déclarer la quantité")}
              </Button>
            )}
            {volumeDeclared && (
              <Button
                priority="secondary"
                onClick={() => setVolumeDeclared(false)}
              >
                {t("Modifier")}
              </Button>
            )}
          </>
        }
        stateRelatedMessage={t(
          "Nous pourrons ensuite vous indiquer les tC02 évitées équivalentes pour cette quantité."
        )}
        state={volumeDeclared ? "default" : "info"}
        disabled={volumeDeclared || mutation.loading}
      />
      {volumeDeclared &&
        value.avoided_emissions_min &&
        value.avoided_emissions_max && (
          <>
            <Notice noColor variant="info">
              <Trans
                components={{ strong: <strong /> }}
                t={t}
                values={{
                  volume: value.volume,
                  min: formatNumber(value.avoided_emissions_min, 0),
                  max: formatNumber(value.avoided_emissions_max, 0),
                }}
                defaults="Pour une quantité de <strong>{{volume}} litres</strong>, vous pouvez enregistrer entre <strong>{{min}} et {{max}} tC02 évitées</strong>."
              />
            </Notice>
            <NumberInput
              label={
                t("Saisir un montant en tCO2 évitées") +
                (volumeDeclared
                  ? ` (${t("entre {{min}} et {{max}}", {
                      min: formatNumber(value.avoided_emissions_min, 0),
                      max: formatNumber(value.avoided_emissions_max, 0),
                    })})`
                  : "")
              }
              min={roundNumber(value.avoided_emissions_min, 0)}
              max={roundNumber(value.avoided_emissions_max, 0)}
              {...bind("avoided_emissions")}
            />
          </>
        )}
    </>
  )
}
