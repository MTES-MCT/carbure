import { useCallback, useEffect, useState } from "react"
import { useSearchParams, createSearchParams } from "react-router-dom"
import { useTranslation } from "react-i18next"
import { Filter, FilterSelection, Status } from "../types"
import * as api from "../api"
import { LotQuery } from "../hooks/lot-query"
import { Option } from "common-v2/utils/normalize"
import { Grid, Row } from "common-v2/components/scaffold"
import { MultiSelect, MultiSelectProps } from "common-v2/components/multi-select" // prettier-ignore
import Button from "common-v2/components/button"

export interface FiltersProps {
  status: Status
  query: LotQuery
  selected: FilterSelection
  onSelect: (field: Filter, value: string[]) => void
}

export const Filters = ({
  status,
  query,
  selected,
  onSelect,
}: FiltersProps) => {
  const { t } = useTranslation()

  // prettier-ignore
  const getFilters = status === 'stocks'
    ? api.getStockFilters
    : api.getLotFilters

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
      {filtersByStatus[status].map((field) => (
        <FilterSelect
          key={field}
          field={field}
          query={query}
          placeholder={filterLabels[field]}
          value={selected[field]}
          onChange={(value) => onSelect(field, value ?? [])}
          getOptions={() => getFilters(field, query)}
        />
      ))}
    </Grid>
  )
}

interface ResetButtonProps {
  filters: FilterManager
}

export const ResetButton = ({ filters }: ResetButtonProps) => {
  const { t } = useTranslation()
  return (
    <Row asideX>
      <Button
        variant="link"
        action={filters.resetFilters}
        label={t("Réinitialiser les filtres")}
      />
      <span> ({filters.count})</span>
    </Row>
  )
}

export interface FilterManager {
  count: number
  selected: FilterSelection
  onFilter: (filter: Filter, value: string[]) => void
  resetFilters: () => void
}

export function useFilters(): FilterManager {
  const [searchParams, setSearchParams] = useSearchParams()
  const [selected, setFilters] = useState<FilterSelection>({})

  useEffect(() => {
    const normalizedFilters = createSearchParams(selected)
    if (normalizedFilters.toString() !== searchParams.toString()) {
      setFilters(searchToFilters(searchParams))
    }
  }, [selected, searchParams])

  const onFilter = useCallback(
    (filter: Filter, value: string[]) => {
      setFilters((filters) => ({ ...filters, [filter]: value }))
      setSearchParams({ ...selected, [filter]: value })
    },
    [selected, setSearchParams]
  )

  const resetFilters = () => setSearchParams({})

  const count = Object.values(selected).filter((list) => list.length > 0).length

  return { count, selected, onFilter, resetFilters }
}

export type FilterSelectProps = { field: Filter; query: LotQuery } & Omit<
  MultiSelectProps<Option, string>,
  "options"
>

export const FilterSelect = ({
  field,
  query,
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
  />
)

export function searchToFilters(search: URLSearchParams) {
  const filters: FilterSelection = {}
  search.forEach((value, filter) => {
    const fkey = filter as Filter
    filters[fkey] = filters[fkey] ?? []
    filters[fkey]!.push(value)
  })
  return filters
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
  Filter.Suppliers,
  Filter.ProductionSites,
  Filter.DeliverySites,
]

const STOCK_FILTERS = [
  Filter.Periods,
  Filter.Biofuels,
  Filter.Feedstocks,
  Filter.CountriesOfOrigin,
  Filter.Suppliers,
  Filter.ProductionSites,
  Filter.Depots,
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

const filtersByStatus: Record<Status, Filter[]> = {
  drafts: DRAFT_FILTERS,
  in: IN_FILTERS,
  stocks: STOCK_FILTERS,
  out: OUT_FILTERS,
  admin: ADMIN_FILTERS,
  unknown: [],
}

export default Filters
