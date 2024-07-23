import { useMemo } from "react"
import { useSearchParams } from "react-router-dom"
import { SafFilter, SafFilterSelection } from "../types"

export function useFilterSearchParams() {
	const [filtersParams, setFiltersParams] = useSearchParams()
	const filters = useMemo(() => {
		const filters: SafFilterSelection = {}
		filtersParams.forEach((value, filter) => {
			const fkey = filter as SafFilter
			filters[fkey] = filters[fkey] ?? []
			filters[fkey]!.push(value)
		})
		return filters
	}, [filtersParams])
	return [filters, setFiltersParams] as [typeof filters, typeof setFiltersParams] // prettier-ignore
}
