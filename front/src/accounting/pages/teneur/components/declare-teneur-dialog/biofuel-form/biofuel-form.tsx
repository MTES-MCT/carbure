import { getBalancesCategory } from "../../../api"
import { Autocomplete } from "common/components/autocomplete2"
import { useFormContext } from "common/components/form2"
import { Step } from "common/components/stepper"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { CategoryEnum, ExtendedUnit } from "common/types"
import i18next from "i18next"
import { useTranslation } from "react-i18next"
import {
  ceilNumber,
  CONVERSIONS,
  floorNumber,
  formatUnit,
} from "common/utils/formatters"
import { Balance } from "accounting/types"
import { DoubleRange } from "common/components/inputs2"
import { debounce } from "common/utils/functions"
import { useEffect, useState } from "react"
import { Notice } from "common/components/notice"

export type BiofuelFormProps = {
  balance?: Balance
  gesBoundMin?: number
  gesBoundMax?: number
}

type BiofuelFormComponentProps = {
  category: CategoryEnum
}

const debouncedGetBalancesCategory = debounce(getBalancesCategory, 200)

export const BiofuelForm = ({ category }: BiofuelFormComponentProps) => {
  const entity = useEntity()
  const { t } = useTranslation()
  const { value, bind, setField } = useFormContext<BiofuelFormProps>()

  const [fullBalance, setFullBalance] = useState<Balance | undefined>(undefined)

  // run the balance query without filtering GHG reduction to get the full range
  const fullBalances = useQuery(getBalancesCategory, {
    key: "biofuels-category",
    params: [entity.id, category],
  })

  // rerun the balance query when changing GHG bounds in order to get the real available balance
  const filteredBalances = useQuery(debouncedGetBalancesCategory, {
    key: "biofuels-category",
    params: [entity.id, category, value.gesBoundMin, value.gesBoundMax],
  })

  const ghgReductionMin = floorNumber(fullBalance?.ghg_reduction_min ?? 50, 1)
  const ghgReductionMax = ceilNumber(fullBalance?.ghg_reduction_max ?? 100, 1)

  function onBalanceChange(balance: Balance | undefined) {
    setField("gesBoundMin", floorNumber(balance?.ghg_reduction_min ?? 50, 0))
    setField("gesBoundMax", ceilNumber(balance?.ghg_reduction_max ?? 100, 0))
    setFullBalance(balance)
  }

  useEffect(() => {
    let newBalance = filteredBalances.result?.data.results.find(
      (b) => b.biofuel.code === fullBalance?.biofuel.code
    )
    if (newBalance) {
      newBalance = {
        ...newBalance,
        available_balance: CONVERSIONS.energy.MJ_TO_GJ(
          newBalance.available_balance
        ),
      }
    }
    setField("balance", newBalance)
  }, [fullBalance, filteredBalances.result, setField])

  return (
    <>
      <Autocomplete
        label={t("Sélectionnez un biocarburant")}
        placeholder={t("Ex: EMHV")}
        options={fullBalances.result?.data?.results ?? []}
        normalize={(balance) => ({
          value: balance,
          label: balance.biofuel.code,
        })}
        loading={fullBalances.loading}
        required
        filter={() => true} // show all options
        value={fullBalance}
        onChange={onBalanceChange}
      />

      {ghgReductionMin !== ghgReductionMax ? (
        <>
          <DoubleRange
            disabled={fullBalance === undefined}
            step={0.1}
            min={ghgReductionMin}
            max={ghgReductionMax}
            suffix="%"
            label={t("Définissez le taux de réduction GES des lots à prélever")}
            minRange={bind("gesBoundMin")}
            maxRange={bind("gesBoundMax")}
          />

          <Notice noColor variant="info">
            {t("Solde disponible pour ces taux de réduction")}
            {" : "}
            <b>
              {formatUnit(
                value.balance?.available_balance ?? 0,
                ExtendedUnit.GJ,
                {
                  fractionDigits: 0,
                }
              )}
            </b>
          </Notice>
        </>
      ) : (
        <Notice noColor variant="info">
          {t("Solde disponible")}
          {" : "}
          <b>
            {formatUnit(
              value.balance?.available_balance ?? 0,
              ExtendedUnit.GJ,
              {
                fractionDigits: 0,
              }
            )}
          </b>
          <br />
          {t("Pour un taux de réduction GES de")}
          {" : "}
          <b>{ghgReductionMin}%</b>
        </Notice>
      )}
    </>
  )
}

export const biofuelFormStepKey = "biofuel"
type BiofuelFormStepKey = typeof biofuelFormStepKey

const allowNextStep = (values: BiofuelFormProps) => {
  return Boolean(values.balance)
}

export const biofuelFormStep: (
  values: BiofuelFormProps
) => Step<BiofuelFormStepKey> = (values) => {
  return {
    key: biofuelFormStepKey,
    title: i18next.t("Biocarburant"),
    allowNextStep: allowNextStep(values),
  }
}
