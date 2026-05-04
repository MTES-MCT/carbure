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
import { useEffect, useState } from "react"
import { useTranslation } from "react-i18next"
import { Unit } from "common/types"

export const AdvancedFiltersBalance = ({
  balance,
  onFiltersChange,
  selected,
}: {
  balance: Balance
  onFiltersChange: (filters: QueryFilters) => void
  selected: Filters
}) => {
  const { t } = useTranslation()
  const { getFilterOptions, filterNormalizers, filterLabels } =
    useAdvancedFiltersBalance({ balance })

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
  balance,
  unit,
}: {
  balance: Balance
  // By default, the unit is the entity preferred unit, but in some cases, it can be overridden
  unit?: Unit
}) => {
  const { value, setField } = useFormContext<AdvancedFiltersFormProps>()
  const [_balance, setBalance] = useState<Balance>(balance)

  const { loading, getBalance } = useAvailableBalance({
    initialBalance: _balance,
    unit,
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

        setBalance({
          ...balance,
          ghg_reduction_min: ghgReductionMin,
          ghg_reduction_max: ghgReductionMax,
        })
      }
    })
  }

  const { selected, onSelect, resetFilters } = useBuildFilters({
    onFiltersChange,
  })

  // When the balance prop changes, reset the local balance state and the filters
  useEffect(() => {
    setBalance(balance)
    resetFilters()
  }, [balance, resetFilters, getBalance])

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
        unit={unit}
      />
    </Box>
  )
}
