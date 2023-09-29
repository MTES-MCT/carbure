import { ElecAdminTransferCertificateFilter, ElecAdminTransferCertificateFilterSelection } from "elec-admin/types"
import { ElecCPOTransferCertificateFilter, ElecCPOTransferCertificateFilterSelection } from "elec/types-cpo"
import { useMemo } from "react"
import { useSearchParams } from "react-router-dom"

export function useFilterSearchParams() {
    const [filtersParams, setFiltersParams] = useSearchParams()
    const filters = useMemo(
        () => {
            const filters: ElecCPOTransferCertificateFilterSelection = {}
            filtersParams.forEach((value, filter) => {
                const fkey = filter as ElecCPOTransferCertificateFilter
                filters[fkey] = filters[fkey] ?? []
                filters[fkey]!.push(value)
            })
            return filters
        },
        [filtersParams]
    )
    return [filters, setFiltersParams] as [typeof filters, typeof setFiltersParams] // prettier-ignore
}


