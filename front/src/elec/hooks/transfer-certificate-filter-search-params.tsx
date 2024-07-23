import { ElecTransferCertificateFilter } from "elec/types"
import { ElecTransferCertificateFilterSelection } from "elec/types-cpo"
import { useMemo } from "react"
import { useSearchParams } from "react-router-dom"

export function useFilterSearchParams() {
	const [filtersParams, setFiltersParams] = useSearchParams()
	const filters = useMemo(() => {
		const filters: ElecTransferCertificateFilterSelection = {}
		filtersParams.forEach((value, filter) => {
			const fkey = filter as ElecTransferCertificateFilter
			filters[fkey] = filters[fkey] ?? []
			filters[fkey]!.push(value)
		})
		return filters
	}, [filtersParams])
	return [filters, setFiltersParams] as [typeof filters, typeof setFiltersParams] // prettier-ignore
}
