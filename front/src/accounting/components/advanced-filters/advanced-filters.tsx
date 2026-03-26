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

export const AdvancedFiltersBalance = ({ balance }: { balance: Balance }) => {
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
  const { value } = useFormContext<AdvancedFiltersFormProps>()
  const _hasFiltersSelected = hasFiltersSelected(value)

  return (
    <Box>
      <div style={{ maxWidth: "600px" }}>
        <GHGRangeForm
          balance={balance}
          ghgReductionMin={_hasFiltersSelected ? value.gesBoundMin : undefined}
          ghgReductionMax={_hasFiltersSelected ? value.gesBoundMax : undefined}
        />
      </div>
      <AdvancedFiltersBalance balance={balance} />

      <AvailableBalance balance={balance} />
    </Box>
  )
}
