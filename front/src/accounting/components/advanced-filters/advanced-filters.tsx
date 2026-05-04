import { Box } from "common/components/scaffold"
import { Text } from "common/components/text"
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
import {
  AdvancedFiltersFormProps,
  AdvancedFiltersWithBalanceFormProps,
  Filters,
} from "./advanced-filters.types"
import { useAvailableBalance } from "./available-balance.hooks"

import { useTranslation } from "react-i18next"
import { ExtendedUnitType } from "common/types"

export const AdvancedFiltersBalance = ({
  onFiltersChange,
  selected,
}: {
  onFiltersChange: (filters: QueryFilters) => void
  selected: Filters
}) => {
  const { t } = useTranslation()
  const { getFilterOptions, filterNormalizers, filterLabels } =
    useAdvancedFiltersBalance()

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
  unit,
}: {
  // By default, the unit is the entity preferred unit, but in some cases, it can be overridden
  unit?: ExtendedUnitType
}) => {
  const { value, setField } =
    useFormContext<AdvancedFiltersWithBalanceFormProps>()

  const { loading, getBalance } = useAvailableBalance({
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
      <AdvancedFiltersBalance onFiltersChange={onSelect} selected={selected} />

      <GHGRangeForm
        balance={value.balance}
        onRangeChange={(gesBoundMin, gesBoundMax) => {
          getBalance({ ...value, gesBoundMin, gesBoundMax })
        }}
      />

      <AvailableBalance
        loading={loading}
        availableBalance={
          value.availableBalance ?? value.balance.available_balance
        }
        unit={unit}
      />
    </Box>
  )
}
