import { Box } from "common/components/scaffold"
import { Text } from "common/components/text"
import {
  isFilterRemoved,
  useAdvancedFiltersBalance,
  useBuildFilters,
} from "./advanced-filters.hooks"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import { useFormContext } from "common/components/form2"
import { Balance } from "accounting/types"
import { QueryFilters } from "common/hooks/query-builder-2"
import { formatGhgReduction, GHGRangeForm } from "../ghg-range-form"
import { AvailableBalance } from "./available-balance"
import { AdvancedFiltersFormProps, Filters } from "./advanced-filters.types"
import { useAvailableBalance } from "./available-balance.hooks"
import { useState } from "react"
export const AdvancedFiltersBalance = ({
  balance,
  onFiltersChange,
  selected,
}: {
  balance: Balance
  onFiltersChange: (filters: QueryFilters) => void
  selected: Filters
}) => {
  const { getFilterOptions, filterNormalizers, filterLabels } =
    useAdvancedFiltersBalance({ balance })

  return (
    <div>
      <Text margin> Filtres avancés </Text>
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
  balance,
}: {
  balance: Balance
}) => {
  const { value, setField } = useFormContext<AdvancedFiltersFormProps>()
  const [_balance, setBalance] = useState<Balance>(balance)

  const { loading, getBalance } = useAvailableBalance({
    initialBalance: balance,
  })

  const onFiltersChange = (
    filters: AdvancedFiltersFormProps,
    previousFilters: Filters
  ) => {
    const _isFilterRemoved = isFilterRemoved(previousFilters, filters)

    // When filters are selected, use the ghg reduction from the range slider
    // Otherwise, use the default ghg reduction from the initial balance
    getBalance({ ...filters }).then((newBalance) => {
      // getBalance({ ...filters, gesBoundMin, gesBoundMax }).then((newBalance) => {
      if (newBalance) {
        const { ghgReductionMin, ghgReductionMax } = formatGhgReduction(
          newBalance.ghg_reduction_min,
          newBalance.ghg_reduction_max
        )

        // When a filter is removed or the new balance values are higher/lower than the previous values,
        // set gesBoundMin/gesBoundMax to the new balance values
        if (
          _isFilterRemoved ||
          (value?.gesBoundMin && value.gesBoundMin < ghgReductionMin)
        )
          setField("gesBoundMin", ghgReductionMin)
        if (
          _isFilterRemoved ||
          (value?.gesBoundMax && value.gesBoundMax > ghgReductionMax)
        )
          setField("gesBoundMax", ghgReductionMax)

        setBalance({
          ...balance,
          ghg_reduction_min: ghgReductionMin,
          ghg_reduction_max: ghgReductionMax,
        })
      }
    })
  }

  const { selected, onSelect } = useBuildFilters({ onFiltersChange })

  return (
    <Box>
      <AdvancedFiltersBalance
        balance={_balance}
        onFiltersChange={onSelect}
        selected={selected}
      />

      <GHGRangeForm
        balance={_balance}
        onRangeChange={(gesBoundMin, gesBoundMax) => {
          getBalance({ ...value, gesBoundMin, gesBoundMax })
        }}
      />

      <AvailableBalance
        loading={loading}
        availableBalance={value.availableBalance ?? _balance.available_balance}
      />
    </Box>
  )
}
