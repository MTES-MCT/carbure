import { useFormContext } from "common/components/form2"
import { Autocomplete } from "common/components/autocomplete2"
import { Trans, useTranslation } from "react-i18next"
import { Notice } from "common/components/notice"
import { getDepotsWithBalance } from "./api"
import useEntity from "common/hooks/entity"
import { Balance } from "accounting/types"
import { OperationText } from "accounting/components/operation-text"
import { useUnit } from "common/hooks/unit"
import { FromDepotFormProps } from "./from-depot-form.types"
import { DoubleRange } from "common/components/inputs2"
import { useQuery } from "common/hooks/async"
import { debounce } from "common/utils/functions"
import { useEffect } from "react"

// Type of the component
type FromDepotProps = {
  balance: Balance
}

const debouncedGetDepotsWithBalance = debounce(getDepotsWithBalance, 200)

export const FromDepotForm = ({ balance }: FromDepotProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { formatUnit } = useUnit()
  const { value, bind, setField } = useFormContext<FromDepotFormProps>()

  const depots = useQuery(
    (sector, customs_category, biofuel, gesBoundMin, gesBoundMax) =>
      debouncedGetDepotsWithBalance(entity.id, {
        sector: sector,
        category: customs_category,
        biofuel: biofuel ?? "",
        ges_bound_min: gesBoundMin,
        ges_bound_max: gesBoundMax,
      }),
    {
      key: "cession-depots",
      params: [
        balance.sector,
        balance.customs_category,
        balance.biofuel.code,
        value.gesBoundMin,
        value.gesBoundMax,
      ] as const,
    }
  )

  useEffect(() => {
    const newDepot = depots.result?.find((b) => b.id === value.from_depot?.id)
    setField("from_depot", newDepot)
  }, [depots.result, setField, value.from_depot?.id])

  return (
    <>
      <DoubleRange
        step={0.1}
        min={Math.floor(balance.ghg_reduction_min)}
        max={Math.ceil(balance.ghg_reduction_max)}
        suffix="%"
        label={t("Définissez le taux de réduction GES des lots à prélever")}
        minRange={bind("gesBoundMin")}
        maxRange={bind("gesBoundMax")}
      />
      <Autocomplete
        label={t("Sélectionnez un dépôt d'expédition")}
        placeholder={t("Rechercher un dépôt")}
        options={depots.result}
        normalize={(depot) => ({
          label: depot.name,
          value: depot,
        })}
        filter={() => true}
        required
        {...bind("from_depot")}
      >
        {({ data: depot }) => (
          <span>
            <Trans
              components={{ strong: <strong /> }}
              t={t}
              values={{
                depot: depot.name,
                quantity: formatUnit(depot.available_balance, {
                  fractionDigits: 0,
                }),
              }}
              defaults="{{depot}} ({{quantity}} disponibles)"
            />
          </span>
        )}
      </Autocomplete>
      {value.from_depot && (
        <>
          {value.from_depot.available_balance &&
          value.from_depot.available_balance > 0 ? (
            <Notice noColor variant="info">
              <Trans
                components={{ strong: <strong /> }}
                t={t}
                values={{
                  depot: value.from_depot.name,
                  quantity: formatUnit(value.from_depot.available_balance, {
                    fractionDigits: 0,
                  }),
                }}
                defaults="Solde disponible dans le dépôt {{depot}} : <strong>{{quantity}}</strong>"
              />
            </Notice>
          ) : null}
          {value.from_depot.available_balance === 0 ? (
            <Notice noColor variant="warning">
              <Trans
                t={t}
                values={{ depot: value.from_depot.name }}
                defaults="Aucun solde disponible dans le dépôt {{depot}}"
              />
            </Notice>
          ) : null}
        </>
      )}
    </>
  )
}

// Recap form data after the step was submitted
export const FromDepotSummary = ({
  values,
}: {
  values: FromDepotFormProps
}) => {
  const { t } = useTranslation()
  const { formatUnit } = useUnit()
  if (
    !values.from_depot?.available_balance ||
    values.from_depot.available_balance <= 0
  ) {
    return null
  }
  return (
    <>
      <OperationText
        title={t("Dépôt d'expédition")}
        description={values.from_depot?.name ?? ""}
      />
      <OperationText
        title={t("Solde disponible")}
        description={formatUnit(values.from_depot.available_balance, {
          fractionDigits: 0,
        })}
      />
    </>
  )
}
