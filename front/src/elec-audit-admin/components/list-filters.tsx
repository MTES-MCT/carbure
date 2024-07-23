import { MultiSelect, MultiSelectProps } from "common/components/multi-select"; // prettier-ignore
import { Grid } from "common/components/scaffold"
import { defaultNormalizer } from "common/utils/normalize"
import {
  ElecAdminAuditFilter,
  ElecAdminAuditFilterSelection,
} from "elec-audit-admin/types"
import { useTranslation } from "react-i18next"

export interface FiltersProps {
  filters: ElecAdminAuditFilter[]
  selected: ElecAdminAuditFilterSelection
  onSelect: (filters: ElecAdminAuditFilterSelection) => void
  getFilterOptions: (filter: ElecAdminAuditFilter) => Promise<any[]>
}

export function ElecAdminAuditFilters({
  filters,
  selected,
  onSelect,
  getFilterOptions,
}: FiltersProps) {
  const { t } = useTranslation()

  const filterLabels = {
    [ElecAdminAuditFilter.Cpo]: t("Aménageur"),
    [ElecAdminAuditFilter.Quarter]: t("Trimestre"),
  }

  return (
    <Grid>
      {filters.map((filter) => {
        return (
          <FilterSelect
            key={filter}
            field={filter}
            placeholder={filterLabels[filter]}
            value={selected[filter]}
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

export type FilterSelectProps = { field: ElecAdminAuditFilter } & Omit<
  MultiSelectProps<string>,
  "options"
>

export default ElecAdminAuditFilters

export const FilterSelect = ({
  field,
  value = [],
  onChange,
  ...props
}: FilterSelectProps) => (
  <MultiSelect
    {...props}
    clear
    search
    variant="solid"
    value={value}
    onChange={onChange}
    normalize={defaultNormalizer}
    sort={(item) => (item.value === "UNKNOWN" ? "" : item.label)}
  />
)
