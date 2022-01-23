import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { useSearchParams } from "react-router-dom"
import { Filter, FilterSelection } from "../types"
import { Normalizer, Option } from "common-v2/utils/normalize"
import { Grid, Row } from "common-v2/components/scaffold"
import { MultiSelect, MultiSelectProps } from "common-v2/components/multi-select" // prettier-ignore
import Button from "common-v2/components/button"
import {
  normalizeAnomalyFilter,
  normalizeBiofuelFilter,
  normalizeCountryFilter,
  normalizeFeedstockFilter,
} from "common-v2/utils/normalizers"

export interface FiltersProps<Q> {
  query: Q
  filters: Filter[]
  selected: FilterSelection
  onSelect: (filters: FilterSelection) => void
  getFilters: (field: Filter, query: Q) => Promise<Option[]>
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
    [Filter.DeliveryStatus]: t("Livraison"),
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
    [Filter.Forwarded]: t("Lots Transférés"),
    [Filter.Mac]: t("Mises à consommation"),
    [Filter.HiddenByAdmin]: t("Lots ignorés"),
    [Filter.HiddenByAuditor]: t("Lots ignorés"),
    [Filter.ClientTypes]: t("Types de client"),
    [Filter.ShowEmpty]: t("Inclure stocks vides"),
  }

  return (
    <Grid>
      {filters.map((field) => (
        <FilterSelect
          key={field}
          field={field}
          placeholder={filterLabels[field]}
          value={selected[field]}
          onChange={(value) => onSelect({ ...selected, [field]: value ?? [] })}
          getOptions={() => getFilters(field, query)}
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
  MultiSelectProps<Option, string>,
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
    sort={(item) => item.label}
  />
)

const filterNormalizers: Partial<Record<Filter, Normalizer<Option, string>>> = {
  [Filter.Feedstocks]: normalizeFeedstockFilter,
  [Filter.Biofuels]: normalizeBiofuelFilter,
  [Filter.CountriesOfOrigin]: normalizeCountryFilter,
  [Filter.Errors]: normalizeAnomalyFilter,
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
