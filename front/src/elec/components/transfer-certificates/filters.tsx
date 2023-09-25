import * as norm from "carbure/utils/normalizers"
import { MultiSelect, MultiSelectProps } from "common/components/multi-select"; // prettier-ignore
import { Grid } from "common/components/scaffold"
import { Normalizer, defaultNormalizer } from "common/utils/normalize"
import { ElecCPOTransferCertificateFilter, ElecCPOTransferCertificateFilterSelection } from "elec/types";
import { useTranslation } from "react-i18next"


export interface FiltersProps {
    filters: ElecCPOTransferCertificateFilter[]
    selected: ElecCPOTransferCertificateFilterSelection
    onSelect: (filters: ElecCPOTransferCertificateFilterSelection) => void
    getFilterOptions: (filter: ElecCPOTransferCertificateFilter) => Promise<any[]>
}

export function TransferCertificateFilters({
    filters,
    selected,
    onSelect,
    getFilterOptions,
}: FiltersProps) {
    const { t } = useTranslation()

    const filterLabels = {
        [ElecCPOTransferCertificateFilter.Operator]: t("Redevable"),
        [ElecCPOTransferCertificateFilter.TransferDate]: t("Date d’émission"),
        [ElecCPOTransferCertificateFilter.CertificateId]: t("Numéro"),
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

export type FilterSelectProps = { field: ElecCPOTransferCertificateFilter } & Omit<
    MultiSelectProps<string>,
    "options"
>

export default TransferCertificateFilters

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
