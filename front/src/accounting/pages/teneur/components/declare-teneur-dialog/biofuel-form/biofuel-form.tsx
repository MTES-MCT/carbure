import { getBalancesCategory } from "../../../api"
import { Autocomplete } from "common/components/autocomplete2"
import { useFormContext } from "common/components/form2"
import { Step } from "common/components/stepper"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { CategoryEnum } from "common/types"
import i18next from "i18next"
import { useTranslation } from "react-i18next"
import { CONVERSIONS } from "common/utils/formatters"
import { Balance } from "accounting/types"
import { DoubleRange } from "common/components/inputs2"

export type BiofuelFormProps = {
  balance?: Balance
  gesBoundMin?: number
  gesBoundMax?: number
}

type BiofuelFormComponentProps = {
  category: CategoryEnum
}

export const BiofuelForm = ({ category }: BiofuelFormComponentProps) => {
  const entity = useEntity()
  const { t } = useTranslation()
  const { bind } = useFormContext<BiofuelFormProps>()

  const result = useQuery(getBalancesCategory, {
    key: "biofuels-category",
    params: [entity.id, category],
  })

  return (
    <>
      <Autocomplete
        label={t("Sélectionnez un biocarburant")}
        placeholder={t("Ex: EMHV")}
        options={result.result?.data?.results ?? []}
        normalize={(balance) => ({
          value: {
            ...balance,
            available_balance: CONVERSIONS.energy.MJ_TO_GJ(
              balance.available_balance
            ),
          },
          label: balance.biofuel.code,
        })}
        loading={result.loading}
        required
        {...bind("balance")}
      />

      <DoubleRange
        min={50}
        max={125}
        suffix="%"
        label={t("Définissez le taux de réduction GES des lots à prélever")}
        minRange={bind("gesBoundMin")}
        maxRange={bind("gesBoundMax")}
      />
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
