import * as norm from "carbure/utils/normalizers"
import { MultiSelect, MultiSelectProps } from "common/components/multi-select"; // prettier-ignore
import { Grid } from "common/components/scaffold"
import { Normalizer, defaultNormalizer } from "common/utils/normalize"
import { useTranslation } from "react-i18next"
import { ElecAdminProvisionCertificateFilter } from "elec-admin/types";

export interface FiltersProps {
    filters: ElecAdminProvisionCertificateFilter[]
    selected: ElecAdminProvisionCertificateFilterSelection
    onSelect: (filters: ElecAdminProvisionCertificateFilterSelection) => void
    getFilterOptions: (filter: ElecAdminProvisionCertificateFilter) => Promise<any[]>
}

export function ProvisionCertificateFilters({
    filters,
    selected,
    onSelect,
    getFilterOptions,
}: FiltersProps) {
    const { t } = useTranslation()

    const filterLabels = {
        [ElecAdminProvisionCertificateFilter.Cpo]: t("Aménageur"),
        [ElecAdminProvisionCertificateFilter.Quarter]: t("Trimestre"),
        [ElecAdminProvisionCertificateFilter.OperatingUnit]: t("Unité d'exploitation"),
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

export type FilterSelectProps = { field: ElecAdminProvisionCertificateFilter } & Omit<
    MultiSelectProps<string>,
    "options"
>


const filterNormalizers: FilterNormalizers = {
    [ElecAdminProvisionCertificateFilter.Cpo]: norm.normalizeFeedstockFilter,
    [ElecAdminProvisionCertificateFilter.Quarter]: norm.normalizePeriodFilter,
    [ElecAdminProvisionCertificateFilter.OperatingUnit]: norm.normalizeUnknownFilter,
}

export default ProvisionCertificateFilters

export type ElecAdminProvisionCertificateFilterSelection = Partial<Record<ElecAdminProvisionCertificateFilter, string[]>>

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
type FilterNormalizers = Partial<Record<ElecAdminProvisionCertificateFilter, Normalizer<any>>> // prettier-ignore