import { getBalancesCategory } from "../../../api"
import { Autocomplete } from "common/components/autocomplete2"
import { useFormContext } from "common/components/form2"
import { Step } from "common/components/stepper"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { CategoryEnum } from "common/types"
import i18next from "i18next"
import { useTranslation } from "react-i18next"
import { Balance } from "accounting/types"

import { AdvancedFiltersBalanceCard } from "accounting/components/advanced-filters/advanced-filters"
import { Box } from "common/components/scaffold"
import { AdvancedFiltersFormProps } from "accounting/components/advanced-filters/advanced-filters.types"
import { formatGhgReduction } from "accounting/components/ghg-range-form"
import { useBuildFilters } from "accounting/components/advanced-filters/advanced-filters.hooks"
import { useMemo } from "react"
import { showNextStepAdvancedFilters } from "accounting/components/advanced-filters/advanced-filters.utils"
import { floorNumber } from "common/utils/formatters"
import { formatSector } from "accounting/utils/formatters"
import { useCompatibleSectors } from "./biofuel-filters-form.hooks"

export type BiofuelFiltersFormProps = AdvancedFiltersFormProps

type BiofuelFiltersFormComponentProps = {
  category: CategoryEnum
}

export const BiofuelFiltersForm = ({
  category,
}: BiofuelFiltersFormComponentProps) => {
  const entity = useEntity()
  const { t } = useTranslation()

  const { resetFilters } = useBuildFilters({})
  const { value, setField } = useFormContext<BiofuelFiltersFormProps>()

  // run the balance query without filtering GHG reduction to get the full range
  const fullBalances = useQuery(getBalancesCategory, {
    key: "biofuels-category",
    params: [entity.id, category],
  })

  // Keep the autocomplete value aligned with currently available options,
  // otherwise label resolution can fail after step transitions.
  const selectedBalance = useMemo(() => {
    const balances = fullBalances.result?.data?.results ?? []
    const selectedBiofuelCode = value.balance?.biofuel?.code
    if (!selectedBiofuelCode) return undefined

    return (
      balances.find(
        (balance) => balance.biofuel?.code === selectedBiofuelCode
      ) ?? value.balance
    )
  }, [fullBalances.result?.data?.results, value.balance])

  // When a biofuel is select, reset the current balance to be used for the advanced filters,
  // and reset the bounds for the GHG range slider + available balance
  function onBalanceChange(balance: Balance | undefined) {
    if (!balance) return
    const { ghgReductionMin, ghgReductionMax } = formatGhgReduction(
      balance.ghg_reduction_min,
      balance.ghg_reduction_max
    )

    const availableBalance =
      floorNumber(balance.available_balance, 0) > 0
        ? balance.available_balance
        : 0
    setField("availableBalance", availableBalance)
    setField("gesBoundMin", ghgReductionMin)
    setField("gesBoundMax", ghgReductionMax)

    // Used to know which balance is currently selected
    setField("balance", balance)
    setField("objective_sector", balance.sector)
    resetFilters()
  }

  const sectors = useCompatibleSectors(value.balance)

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
          value={selectedBalance}
          onChange={onBalanceChange}
        />
        {value.balance && (
          <Autocomplete
            label={t("Filière")}
            options={sectors.map((sector) => ({
              value: sector,
              label: formatSector(sector),
            }))}
            value={value.objective_sector}
            onChange={(option) => setField("objective_sector", option)}
            readOnly={sectors.length === 1}
            required
          />
        )}
      </Box>
      {value.balance && <AdvancedFiltersBalanceCard />}
    </>
  )
}

export const biofuelFiltersFormStepKey = "biofuel-filters"
type BiofuelFiltersFormStepKey = typeof biofuelFiltersFormStepKey

export const biofuelFiltersFormStep: (
  values: BiofuelFiltersFormProps
) => Step<BiofuelFiltersFormStepKey> = (values) => {
  return {
    key: biofuelFiltersFormStepKey,
    title: i18next.t("Biocarburant"),
    allowNextStep: showNextStepAdvancedFilters(values),
  }
}
