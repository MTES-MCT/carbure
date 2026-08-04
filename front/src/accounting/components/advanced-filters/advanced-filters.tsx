import { Box } from "common/components/scaffold"
import { Text } from "common/components/text"
import { Balance } from "accounting/types"
import {
  isFilterRemoved,
  useAdvancedFiltersBalance,
  useBuildFilters,
} from "./advanced-filters.hooks"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import { useFormContext } from "common/components/form2"
import { QueryFilters } from "common/hooks/query-builder-2"
import { formatGhgReduction, GHGRangeForm } from "../ghg-range-form"
import { AvailableBalance } from "./available-balance"
import { AdvancedFiltersFormProps, Filters } from "./advanced-filters.types"
import { useAvailableBalance } from "./available-balance.hooks"

import { useTranslation } from "react-i18next"

export const AdvancedFiltersBalance = ({
  onFiltersChange,
  selected,
  balance,
}: {
  onFiltersChange: (filters: QueryFilters) => void
  selected: Filters
  balance: Balance
}) => {
  const { t } = useTranslation()
  const { getFilterOptions, filterNormalizers, filterLabels } =
    useAdvancedFiltersBalance(balance)

  return (
    <div>
      <Text margin> {t("Filtres avancés")} </Text>
      <FilterMultiSelect2
        filterLabels={filterLabels}
        getFilterOptions={getFilterOptions}
        selected={selected}
        onSelect={onFiltersChange}
        normalizers={filterNormalizers}
      />
    </div>
  )
}

export const AdvancedFiltersBalanceCard = ({
  initialBalance,
}: {
  initialBalance?: Balance
}) => {
  const { value } = useFormContext<AdvancedFiltersFormProps>()
  const balance = value.balance ?? initialBalance

  if (!balance) {
    return null
  }

  return <AdvancedFiltersBalanceCardContent balance={balance} />
}

const AdvancedFiltersBalanceCardContent = ({
  balance,
}: {
  balance: Balance
}) => {
  const { value, setField } = useFormContext<AdvancedFiltersFormProps>()

  const { loading, getBalance } = useAvailableBalance({
    balance,
  })

  const onFiltersChange = (
    filters: AdvancedFiltersFormProps,
    previousFilters: Filters
  ) => {
    const _isFilterRemoved = isFilterRemoved(previousFilters, filters)

    // When filters are selected, use the ghg reduction from the range slider
    // Otherwise, use the default ghg reduction from the initial balance
    getBalance({
      ...filters,
      gesBoundMin: _isFilterRemoved ? undefined : value.gesBoundMin,
      gesBoundMax: _isFilterRemoved ? undefined : value.gesBoundMax,
    }).then((newBalance) => {
      if (newBalance) {
        const { ghgReductionMin, ghgReductionMax } = formatGhgReduction(
          newBalance.ghg_reduction_min,
          newBalance.ghg_reduction_max
        )

        setField("gesBoundMin", ghgReductionMin)
        setField("gesBoundMax", ghgReductionMax)

        setField("balance", {
          ...newBalance,
          ghg_reduction_min: ghgReductionMin,
          ghg_reduction_max: ghgReductionMax,
        })
      }
    })
  }

  const { selected, onSelect } = useBuildFilters({
    onFiltersChange,
  })

  return (
    <Box>
      <AdvancedFiltersBalance
        onFiltersChange={onSelect}
        selected={selected}
        balance={balance}
      />

      <GHGRangeForm
        balance={balance}
        onRangeChange={(gesBoundMin, gesBoundMax) => {
          getBalance({ ...value, gesBoundMin, gesBoundMax })
        }}
      />

      <AvailableBalance
        loading={loading}
        availableBalance={value.availableBalance ?? balance.available_balance}
      />
    </Box>
  )
}
