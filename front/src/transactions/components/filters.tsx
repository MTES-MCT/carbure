import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { useSearchParams } from "react-router-dom"
import { Filter, FilterSelection } from "../types"
import { Normalizer } from "common/utils/normalize"
import { Grid, Row } from "common/components/scaffold"
import { MultiSelect, MultiSelectProps } from "common/components/multi-select" // prettier-ignore
import Button from "common/components/button"
import * as norm from "carbure/utils/normalizers"

export interface FiltersProps<Q> {
	query: Q
	filters: Filter[]
	selected: FilterSelection
	onSelect: (filters: FilterSelection) => void
	getFilters: (field: Filter, query: Q) => Promise<any[]>
}

export function Filters<T>({
	query,
	filters,
	selected,
	onSelect,
	getFilters,
}: FiltersProps<T>) {
	const { t } = useTranslation()

	const filterLabels = {
		[Filter.Periods]: t("Périodes"),
		[Filter.ProductionSites]: t("Sites de production"),
		[Filter.Feedstocks]: t("Matières Premières"),
		[Filter.Biofuels]: t("Biocarburants"),
		[Filter.CountriesOfOrigin]: t("Pays d'origine"),
		[Filter.DeliverySites]: t("Sites de livraison"),
		[Filter.Depots]: t("Dépôts"),
		[Filter.Clients]: t("Clients"),
		[Filter.Suppliers]: t("Fournisseurs"),
		[Filter.AddedBy]: t("Ajouté par"),
		[Filter.Errors]: t("Incohérences"),
		[Filter.ClientTypes]: t("Types de client"),
		[Filter.ShowEmpty]: t("Inclure stocks vides"),
		[Filter.DeliveryTypes]: t("Types de livraison"),
		[Filter.LotStatus]: t("Statut"),
		[Filter.CorrectionStatus]: t("Corrections"),
		[Filter.Scores]: t("Score"),
		[Filter.Conformity]: t("Conformité"),
		[Filter.ML]: t("ML"),
	}

	return (
		<Grid>
			{filters.map((filter) => (
				<FilterSelect
					key={filter}
					field={filter}
					placeholder={filterLabels[filter]}
					value={selected[filter]}
					onChange={(value) => onSelect({ ...selected, [filter]: value ?? [] })}
					getOptions={() => getFilters(filter, query)}
				/>
			))}
		</Grid>
	)
}

export interface FilterManager {
	filters: FilterSelection
	onFilter: (filters: FilterSelection) => void
}

export const ResetButton = ({ filters, onFilter }: FilterManager) => {
	const { t } = useTranslation()
	return (
		<Row asideX>
			<Button
				variant="link"
				action={() => onFilter({})}
				label={t("Réinitialiser les filtres")}
			/>
			<span> ({countFilters(filters)})</span>
		</Row>
	)
}

export type FilterSelectProps = { field: Filter } & Omit<
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
		normalize={filterNormalizers[field]}
		sort={(item) => (item.value === "UNKNOWN" ? "" : item.label)}
	/>
)

type FilterNormalizers= Partial<Record<Filter, Normalizer<any>>> // prettier-ignore
const filterNormalizers: FilterNormalizers = {
	[Filter.Feedstocks]: norm.normalizeFeedstockFilter,
	[Filter.Biofuels]: norm.normalizeBiofuelFilter,
	[Filter.CountriesOfOrigin]: norm.normalizeCountryFilter,
	[Filter.Errors]: norm.normalizeAnomalyFilter,
	[Filter.DeliveryTypes]: norm.normalizeDeliveryTypeFilter,
	[Filter.LotStatus]: norm.normalizeLotStatusFilter,
	[Filter.ClientTypes]: norm.normalizeEntityTypeFilter,
	[Filter.Suppliers]: norm.normalizeUnknownFilter,
	[Filter.Clients]: norm.normalizeUnknownFilter,
	[Filter.DeliverySites]: norm.normalizeUnknownFilter,
	[Filter.ProductionSites]: norm.normalizeUnknownFilter,
	[Filter.Depots]: norm.normalizeUnknownFilter,
	[Filter.Periods]: norm.normalizePeriodFilter,
	[Filter.CorrectionStatus]: norm.normalizeCorrectionFilter,
	[Filter.Conformity]: norm.normalizeConformityFilter,
}

export function useFilterParams() {
	const [filtersParams, setFiltersParams] = useSearchParams()
	const filters = useMemo(() => searchToFilters(filtersParams), [filtersParams])
	return [filters, setFiltersParams] as [typeof filters, typeof setFiltersParams] // prettier-ignore
}

export function searchToFilters(search: URLSearchParams) {
	const filters: FilterSelection = {}
	search.forEach((value, filter) => {
		const fkey = filter as Filter
		filters[fkey] = filters[fkey] ?? []
		filters[fkey]!.push(value)
	})
	return filters
}

export function countFilters(filters: FilterSelection | undefined) {
	if (filters === undefined) return 0
	return Object.values(filters).reduce((total, list) => total + list.length, 0)
}

export default Filters
