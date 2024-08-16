import { MultiSelect, MultiSelectProps } from "common/components/multi-select"; // prettier-ignore
import { Grid } from "common/components/scaffold";
import { defaultNormalizer } from "common/utils/normalize";
import { ElecAuditorApplicationsFilter, ElecAuditorApplicationsFilterSelection } from "elec-auditor/types";
import { useTranslation } from "react-i18next";

export interface FiltersProps {
    filters: ElecAuditorApplicationsFilter[]
    selected: ElecAuditorApplicationsFilterSelection
    onSelect: (filters: ElecAuditorApplicationsFilterSelection) => void
    getFilterOptions: (filter: ElecAuditorApplicationsFilter) => Promise<any[]>
}

export function ApplicationsFilters({
    filters,
    selected,
    onSelect,
    getFilterOptions,
}: FiltersProps) {
    const { t } = useTranslation()

    const filterLabels = {
        [ElecAuditorApplicationsFilter.Cpo]: t("Aménageur"),
    }

    return (
        <Grid>
            {filters.map((filter) => {
                return <FilterSelect
                    key={filter}
                    field={filter}
                    placeholder={filterLabels[filter]}
                    value={selected[filter]}
                    onChange={(value) => onSelect({ ...selected, [filter]: value ?? [] })}
                    getOptions={() => getFilterOptions(filter)}
                />
            }
            )}
        </Grid>
    )
}

export default ApplicationsFilters


export type FilterSelectProps = { field: ElecAuditorApplicationsFilter } & Omit<
    MultiSelectProps<string>,
    "options"
>

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
