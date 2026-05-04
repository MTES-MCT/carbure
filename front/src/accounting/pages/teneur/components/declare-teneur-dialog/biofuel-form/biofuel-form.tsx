import { getBalancesCategory } from "../../../api"
import { Autocomplete } from "common/components/autocomplete2"
import { useFormContext } from "common/components/form2"
import { Step } from "common/components/stepper"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { CategoryEnum, ExtendedUnit } from "common/types"
import i18next from "i18next"
import { useTranslation } from "react-i18next"
import { Balance } from "accounting/types"

import { AdvancedFiltersBalanceCard } from "accounting/components/advanced-filters/advanced-filters"
import { Box } from "common/components/scaffold"
import { AdvancedFiltersFormProps } from "accounting/components/advanced-filters/advanced-filters.types"
import { formatGhgReduction } from "accounting/components/ghg-range-form"
import { useState } from "react"

export type BiofuelFormProps = AdvancedFiltersFormProps & {
  balance?: Balance
}

type BiofuelFormComponentProps = {
  category: CategoryEnum
}

export const BiofuelForm = ({ category }: BiofuelFormComponentProps) => {
  const entity = useEntity()
  const { t } = useTranslation()
  const { value, setField } = useFormContext<BiofuelFormProps>()

  const [fullBalance, setFullBalance] = useState<Balance | undefined>(
    value.balance ?? undefined
  )

  // run the balance query without filtering GHG reduction to get the full range
  const fullBalances = useQuery(getBalancesCategory, {
    key: "biofuels-category",
    params: [entity.id, category],
  })

  // When a biofuel is select, reset the current balance to be used for the advanced filters,
  // and reset the bounds for the GHG range slider + available balance
  function onBalanceChange(balance: Balance | undefined) {
    if (!balance) return
    const { ghgReductionMin, ghgReductionMax } = formatGhgReduction(
      balance.ghg_reduction_min,
      balance.ghg_reduction_max
    )

    setFullBalance(balance)

    setField("availableBalance", balance.available_balance)
    setField("gesBoundMin", ghgReductionMin)
    setField("gesBoundMax", ghgReductionMax)

    // Used to know which balance is currently selected
    setField("balance", balance)
  }

  return (
    <>
      <Box spacing="md">
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
      </Box>
      {fullBalance && (
        <AdvancedFiltersBalanceCard
          balance={fullBalance}
          unit={ExtendedUnit.GJ}
        />
      )}
    </>
  )
}

export const biofuelFormStepKey = "biofuel"
type BiofuelFormStepKey = typeof biofuelFormStepKey

export const biofuelFormStep: (
  values: BiofuelFormProps
) => Step<BiofuelFormStepKey> = () => {
  return {
    key: biofuelFormStepKey,
    title: i18next.t("Biocarburant"),
  }
}
