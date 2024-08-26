import { MultiSelect } from "common/components/multi-select"; // prettier-ignore
import { Grid } from "common/components/scaffold";
import { CBFilterSelection } from "common/hooks/query-builder";
import { defaultNormalizer } from "common/utils/normalize";

export interface FilterMultiSelectProps {
  filterLabels: Record<string, string>
  selected: CBFilterSelection
  onSelect: (filters: CBFilterSelection) => void
  getFilterOptions: (filter: string) => Promise<any[]>
}

export function FilterMultiSelect({
  filterLabels,
  selected,
  onSelect,
  getFilterOptions,
}: FilterMultiSelectProps) {

  const filters = Object.keys(filterLabels)

  return (
    <Grid>
      {filters.map((filter) => {
        return (
          <MultiSelect
            key={filter}
            clear
            search
            variant="solid"
            value={selected[filter]}
            placeholder={filterLabels[filter]}
            normalize={defaultNormalizer}
            sort={(item) => (item.value === "UNKNOWN" ? "" : item.label)}
            onChange={(value) =>
              onSelect({ ...selected, [filter]: value ?? [] })
            }
            getOptions={() => getFilterOptions(filter)}

          />
        )
      })}
    </Grid>
  )
}

export default FilterMultiSelect
