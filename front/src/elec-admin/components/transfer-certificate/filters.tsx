import { MultiSelect, MultiSelectProps } from "common/components/multi-select"; // prettier-ignore
import { Grid } from "common/components/scaffold";
import { defaultNormalizer } from "common/utils/normalize";
import { ElecAdminTransferCertificateFilter, ElecAdminTransferCertificateFilterSelection } from "elec-admin/types";
import { useTranslation } from "react-i18next";

export interface FiltersProps {
    filters: ElecAdminTransferCertificateFilter[]
    selected: ElecAdminTransferCertificateFilterSelection
    onSelect: (filters: ElecAdminTransferCertificateFilterSelection) => void
    getFilterOptions: (filter: ElecAdminTransferCertificateFilter) => Promise<any[]>
}

export function TransferCertificateFilters({
    filters,
    selected,
    onSelect,
    getFilterOptions,
}: FiltersProps) {
    const { t } = useTranslation()

    const filterLabels = {
        [ElecAdminTransferCertificateFilter.Cpo]: t("Aménageur"),
        [ElecAdminTransferCertificateFilter.Operator]: t("Redevable"),
        [ElecAdminTransferCertificateFilter.TransferDate]: t("Date d’émission"),
        [ElecAdminTransferCertificateFilter.CertificateId]: t("Numéro"),

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

export type FilterSelectProps = { field: ElecAdminTransferCertificateFilter } & Omit<
    MultiSelectProps<string>,
    "options"
>


// const filterNormalizers: FilterNormalizers = {
//     [ElecAdminTransferCertificateFilter.Cpo]: norm.normalizeFeedstockFilter,
//     [ElecAdminTransferCertificateFilter.Operator]: norm.normalizePeriodFilter,
//     [ElecAdminTransferCertificateFilter.TransferDate]: norm.normalizeUnknownFilter,
//     [ElecAdminTransferCertificateFilter.CertificateId]: norm.normalizeUnknownFilter,
// }

export default TransferCertificateFilters


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
// type FilterNormalizers = Partial<Record<ElecAdminTransferCertificateFilter, Normalizer<any>>> // prettier-ignore