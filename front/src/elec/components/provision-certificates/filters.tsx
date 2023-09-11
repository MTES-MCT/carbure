import * as norm from "carbure/utils/normalizers"
import { MultiSelect, MultiSelectProps } from "common/components/multi-select"; // prettier-ignore
import { Grid } from "common/components/scaffold"
import { Normalizer, defaultNormalizer } from "common/utils/normalize"
import { useTranslation } from "react-i18next"
import { ElecCPOProvisionCertificateFilter, ElecCPOProvisionCertificateFilterSelection } from "elec/types";

export interface FiltersProps {
    filters: ElecCPOProvisionCertificateFilter[]
    selected: ElecCPOProvisionCertificateFilterSelection
    onSelect: (filters: ElecCPOProvisionCertificateFilterSelection) => void
    getFilterOptions: (filter: ElecCPOProvisionCertificateFilter) => Promise<any[]>
}

export function ProvisionCertificateFilters({
    filters,
    selected,
    onSelect,
    getFilterOptions,
}: FiltersProps) {
    const { t } = useTranslation()

    const filterLabels = {
        [ElecCPOProvisionCertificateFilter.Quarter]: t("Trimestre"),
        [ElecCPOProvisionCertificateFilter.OperatingUnit]: t("Unité d'exploitation"),
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

export type FilterSelectProps = { field: ElecCPOProvisionCertificateFilter } & Omit<
    MultiSelectProps<string>,
    "options"
>


const filterNormalizers: FilterNormalizers = {
    [ElecCPOProvisionCertificateFilter.Quarter]: norm.normalizePeriodFilter,
    [ElecCPOProvisionCertificateFilter.OperatingUnit]: norm.normalizeUnknownFilter,
}

export default ProvisionCertificateFilters


///

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
type FilterNormalizers = Partial<Record<ElecCPOProvisionCertificateFilter, Normalizer<any>>> // prettier-ignore