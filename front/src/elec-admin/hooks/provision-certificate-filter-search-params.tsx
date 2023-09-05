import { ElecAdminProvisionCertificateFilterSelection } from "elec-admin/components/provision-certificates/filters"
import { useMemo } from "react"
import { useSearchParams } from "react-router-dom"
import { ElecAdminProvisionCertificateFilter } from "elec-admin/types"

export function useFilterSearchParams() {
    const [filtersParams, setFiltersParams] = useSearchParams()
    const filters = useMemo(
        () => {
            const filters: ElecAdminProvisionCertificateFilterSelection = {}
            filtersParams.forEach((value, filter) => {
                const fkey = filter as ElecAdminProvisionCertificateFilter
                filters[fkey] = filters[fkey] ?? []
                filters[fkey]!.push(value)
            })
            return filters
        },
        [filtersParams]
    )
    return [filters, setFiltersParams] as [typeof filters, typeof setFiltersParams] // prettier-ignore
}


