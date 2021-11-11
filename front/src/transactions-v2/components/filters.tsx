import { useCallback, useEffect, useState } from "react"
import { useSearchParams, createSearchParams } from "react-router-dom"
import { useTranslation } from "react-i18next"
import { useAsyncCallback, UseAsyncReturn } from "react-async-hook"
import { AxiosResponse } from "axios"
import { Api } from "common-v2/services/api"
import { normalizeTree, Option } from "common-v2/utils/normalize"
import { Grid } from "common-v2/components/scaffold"
import { MultiSelect, MultiSelectProps } from "common-v2/components/multi-select" // prettier-ignore
import { Filter, FilterSelection, LotQuery } from "../types"
import * as api from "../api"
import { Status } from "../hooks/status"

export interface FiltersProps {
  status: Status
  query: LotQuery
  selected: FilterSelection
  onSelect: (field: Filter, value: Option[]) => void
}

export const Filters = ({
  status,
  query,
  selected,
  onSelect,
}: FiltersProps) => {
  const { t } = useTranslation()

  const filterLabels = {
    [Filter.DeliveryStatus]: t("Livraison"),
    [Filter.Periods]: t("Périodes"),
    [Filter.ProductionSites]: t("Sites de production"),
    [Filter.Feedstocks]: t("Matières Premières"),
    [Filter.Biofuels]: t("Biocarburants"),
    [Filter.CountriesOfOrigin]: t("Pays d'origine"),
    [Filter.DeliverySites]: t("Sites de livraison"),
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
      {statusFilters[status].map((field) => (
        <FilterSelect
          key={field}
          field={field}
          query={query}
          placeholder={filterLabels[field]}
          value={selected[field]}
          onChange={(value) => onSelect(field, value ?? [])}
        />
      ))}
    </Grid>
  )
}

export interface FilterManager {
  count: number
  selected: FilterSelection
  onFilter: (filter: Filter, value: Option[]) => void
  resetFilters: () => void
}

export function useFilters(): FilterManager {
  const [searchParams, setSearchParams] = useSearchParams()
  const [selected, setFilters] = useState<FilterSelection>({})

  useEffect(() => {
    const normalizedFilters = createSearchParams(normalizeFilters(selected))
    if (normalizedFilters.toString() !== searchParams.toString()) {
      setFilters(searchToFilters(searchParams))
    }
  }, [selected, searchParams])

  const onFilter = useCallback(
    (filter: Filter, value: Option[]) => {
      setFilters((filters) => ({ ...filters, [filter]: value }))
      setSearchParams(normalizeFilters({ ...selected, [filter]: value }))
    },
    [selected, setSearchParams]
  )

  const resetFilters = () => setFilters({})

  const count = Object.values(selected).filter((list) => list.length > 0).length

  return { count, selected, onFilter, resetFilters }
}

export type FilterSelectProps = { field: Filter; query: LotQuery } & Omit<
  MultiSelectProps<Option>,
  "options"
>

export const FilterSelect = ({
  field,
  query,
  value = [],
  onChange,
  ...props
}: FilterSelectProps) => {
  const options = useAsyncCallback(api.getFilters)
  const sortedOptions = (options.result?.data.data ?? []).sort(sortFilters)

  // if we already have a value set for the filter before the user has opened the dropdown
  // fetch the related options and match the value with them
  if (value.length > 0 && !options.currentPromise) {
    initFilter(field, query, value, options, onChange)
  }

  return (
    <MultiSelect
      {...props}
      clear
      search
      variant="solid"
      loading={options.loading}
      value={value}
      onChange={onChange}
      options={sortedOptions}
      onOpen={() => options.execute(field, query)}
    />
  )
}

export function initFilter(
  field: Filter,
  query: LotQuery,
  value: Option[],
  options: UseAsyncReturn<AxiosResponse<Api<Option[]>>>,
  onChange: (value: Option[]) => void
) {
  options.execute(field, query).then((res) => {
    const filterOptions = res.data.data ?? []
    const normOptions = normalizeTree(filterOptions ?? [])

    const valueKeys = normalizeTree(value ?? []).map((v) => v.key)
    const valueOptions = normOptions.filter((o) => valueKeys.includes(o.key))

    onChange(valueOptions.map((v) => v.value))
  })
}

export function normalizeFilters(filters: FilterSelection) {
  const normalizedFilters: Partial<Record<Filter, string[]>> = {}
  for (const filter in filters) {
    const fkey = filter as Filter
    normalizedFilters[fkey] = filters[fkey]?.map((f) => f.key) ?? []
  }
  return normalizedFilters
}

export function searchToFilters(search: URLSearchParams) {
  const filters: FilterSelection = {}
  search.forEach((key, filter) => {
    const fkey = filter as Filter
    filters[fkey] = filters[fkey] || []
    filters[fkey]!.push({ key, label: key })
  })
  return filters
}

function sortFilters(a: Option, b: Option) {
  return a.label.localeCompare(b.label, "fr")
}

const DRAFT_FILTERS = [
  Filter.Periods,
  Filter.Biofuels,
  Filter.Feedstocks,
  Filter.CountriesOfOrigin,
  Filter.Suppliers,
  Filter.Clients,
  Filter.ProductionSites,
  Filter.DeliverySites,
]

const IN_FILTERS = [
  Filter.Periods,
  Filter.Biofuels,
  Filter.Feedstocks,
  Filter.CountriesOfOrigin,
  Filter.Clients,
  Filter.ProductionSites,
  Filter.DeliverySites,
]

const STOCK_FILTERS = [
  Filter.Periods,
  Filter.Biofuels,
  Filter.Feedstocks,
  Filter.CountriesOfOrigin,
  Filter.Clients,
  Filter.ProductionSites,
  Filter.DeliverySites,
]

const OUT_FILTERS = [
  Filter.Periods,
  Filter.Biofuels,
  Filter.Feedstocks,
  Filter.CountriesOfOrigin,
  Filter.Clients,
  Filter.ProductionSites,
  Filter.DeliverySites,
]

const ADMIN_FILTERS = [
  Filter.Mac,
  Filter.DeliveryStatus,
  Filter.Periods,
  Filter.Biofuels,
  Filter.Feedstocks,
  Filter.CountriesOfOrigin,
  Filter.Suppliers,
  Filter.Clients,
  Filter.ProductionSites,
  Filter.DeliverySites,
  Filter.AddedBy,
  Filter.Forwarded,
  Filter.Errors,
  Filter.HiddenByAdmin,
  Filter.ClientTypes,
]

const statusFilters: Record<Status, Filter[]> = {
  DRAFT: DRAFT_FILTERS,
  IN: IN_FILTERS,
  STOCK: STOCK_FILTERS,
  OUT: OUT_FILTERS,
  ADMIN: ADMIN_FILTERS,
  UNKNOWN: [],
}

export default Filters
