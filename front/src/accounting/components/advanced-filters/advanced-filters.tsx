import { Box } from "common/components/scaffold"
import { Text } from "common/components/text"
import {
  hasFiltersSelected,
  useAdvancedFiltersBalance,
} from "./advanced-filters.hooks"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import { useFormContext } from "common/components/form2"
import { Balance } from "accounting/types"
import { useMemo } from "react"
import { QueryFilters } from "common/hooks/query-builder-2"
import { GHGRangeForm } from "../ghg-range-form"
import { AvailableBalance } from "./available-balance"
import {
  AdvancedFiltersFormProps,
  ADVANCED_FILTER_FIELDS,
  Filters,
} from "./advanced-filters.types"
import { useAvailableBalance } from "./available-balance.hooks"

export const AdvancedFiltersBalance = ({
  balance,
  onFiltersChange,
}: {
  balance: Balance
  onFiltersChange: (filters: AdvancedFiltersFormProps) => void
}) => {
  const { getFilterOptions, filterNormalizers, filterLabels } =
    useAdvancedFiltersBalance({ balance })

  const { value, setField } = useFormContext<AdvancedFiltersFormProps>()

  const selected2: Filters = useMemo(
    () =>
      Object.fromEntries(
        ADVANCED_FILTER_FIELDS.map((filterField) => [
          filterField,
          value[filterField] ?? [],
        ])
      ) as Filters,
    [value]
  )

  const onSelect = (filters: QueryFilters) => {
    Object.entries(filters).forEach(([filter, value]) => {
      setField(filter as keyof AdvancedFiltersFormProps, value ?? [])
    })
    onFiltersChange(filters as unknown as AdvancedFiltersFormProps)
  }

  return (
    <div>
      <Text margin> Filtres avancés </Text>
      <FilterMultiSelect2
        filterLabels={filterLabels}
        getFilterOptions={getFilterOptions}
        selected={selected2}
        onSelect={onSelect}
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
  const { loading, getBalance } = useAvailableBalance({
    initialBalance: balance,
  })

  const onFiltersChange = (filters: AdvancedFiltersFormProps) => {
    const _hasFiltersSelected = hasFiltersSelected(filters)

    const gesBoundMin = _hasFiltersSelected
      ? value.gesBoundMin
      : balance?.ghg_reduction_min
    const gesBoundMax = _hasFiltersSelected
      ? value.gesBoundMax
      : balance?.ghg_reduction_max

    // When filters are selected, use the ghg reduction from the range slider
    // Otherwise, use the default ghg reduction from the initial balance
    getBalance({ ...filters, gesBoundMin, gesBoundMax }).then((data) => {
      // When filters are selected, use the ghg reduction from the new data
      // Otherwise, use the default ghg reduction from the initial balance
      if (_hasFiltersSelected) {
        setField("gesBoundMin", data?.ghg_reduction_min)
        setField("gesBoundMax", data?.ghg_reduction_max)
      } else {
        setField("gesBoundMin", balance?.ghg_reduction_min)
        setField("gesBoundMax", balance?.ghg_reduction_max)
      }
    })
  }

  return (
    <Box>
      <AdvancedFiltersBalance
        balance={balance}
        onFiltersChange={onFiltersChange}
      />
      <div style={{ maxWidth: "600px" }}>
        <GHGRangeForm
          balance={balance}
          onRangeChange={(gesBoundMin, gesBoundMax) => {
            getBalance({ ...value, gesBoundMin, gesBoundMax })
          }}
        />
      </div>

      <AvailableBalance
        loading={loading}
        availableBalance={value.availableBalance ?? balance.available_balance}
      />
    </Box>
  )
}
