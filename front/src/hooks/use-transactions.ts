import { useState, useEffect } from "react"

import { SelectValue } from "../components/system/select"
import { Filters, Lots } from "../services/types"

import { PageSelection, usePageSelection } from "../components/system/pagination" // prettier-ignore
import useAPI from "./helpers/use-api"

import { getStocks, getStockSnapshot } from "../services/lots"

import useEntity, { EntitySelection } from "./helpers/use-entity"

export interface SearchSelection {
  query: string
  setQuery: (s: string) => void
}

// manage search query
function useSearchSelection(pagination: PageSelection): SearchSelection {
  const [query, setQueryState] = useState("")

  function setQuery(query: string) {
    pagination.setPage(0)
    setQueryState(query)
  }

  return { query, setQuery }
}

export interface FilterSelection {
  selected: { [k in Filters]: SelectValue }
  select: (type: Filters, value: SelectValue) => void
  reset: () => void
}

// manage current filter selection
function useFilterSelection(pagination: PageSelection): FilterSelection {
  const [selected, setFilters] = useState<FilterSelection["selected"]>({
    [Filters.Biocarburants]: null,
    [Filters.MatieresPremieres]: null,
    [Filters.CountriesOfOrigin]: null,
    [Filters.Periods]: null,
    [Filters.Clients]: null,
    [Filters.ProductionSites]: null,
    [Filters.DeliverySites]: null,
  })

  function select(type: Filters, value: SelectValue) {
    pagination.setPage(0)
    setFilters({ ...selected, [type]: value })
  }

  function reset() {
    setFilters({
      [Filters.Biocarburants]: null,
      [Filters.MatieresPremieres]: null,
      [Filters.CountriesOfOrigin]: null,
      [Filters.Periods]: null,
      [Filters.Clients]: null,
      [Filters.ProductionSites]: null,
      [Filters.DeliverySites]: null,
    })
  }

  return { selected, select, reset }
}

export interface SortingSelection {
  column: string
  order: "asc" | "desc"
  sortBy: (c: string) => void
}

function useSortingSelection(): SortingSelection {
  const [current, setCurrent] = useState<{
    column: string
    order: "asc" | "desc"
  }>({ column: "", order: "asc" })

  function sortBy(column: string) {
    if (current.column !== column) {
      return setCurrent({ column, order: "asc" })
    } else if (current.column && current.order === "asc") {
      return setCurrent({ column, order: "desc" })
    } else if (current.column && current.order === "desc") {
      return setCurrent({ column: "", order: "asc" })
    }
  }

  return { ...current, sortBy }
}

interface StockHook {
  loading: boolean
  error: string | null
  data: Lots | null
  resolve: () => void
}

function useGetStockSnapshot(entity: EntitySelection) {
  const [snapshot, resolveStockSnapshot] = useAPI(getStockSnapshot)

  function resolve() {
    if (entity !== null) {
      return resolveStockSnapshot(entity).cancel
    }
  }

  useEffect(resolve, [resolveStockSnapshot, entity])

  return { ...snapshot, resolve }
}

// fetches current transaction list when parameters change
function useGetStocks(
  entity: EntitySelection,
  filters: FilterSelection,
  pagination: PageSelection,
  search: SearchSelection,
  sorting: SortingSelection
): StockHook {
  const [transactions, resolveStocks] = useAPI(getStocks)

  function resolve() {
    if (entity !== null) {
      return resolveStocks(
        entity,
        filters.selected,
        pagination.page,
        pagination.limit,
        search.query,
        sorting.column,
        sorting.order
      ).cancel
    }
  }

  useEffect(resolve, [
    resolveStocks,
    entity,
    filters.selected,
    pagination.page,
    pagination.limit,
    search.query,
    sorting.column,
    sorting.order,
  ])

  return { ...transactions, resolve }
}

export function useStocks() {
  const entity = useEntity()

  const sorting = useSortingSelection()
  const pagination = usePageSelection()

  const search = useSearchSelection(pagination)
  const filters = useFilterSelection(pagination)
  const snapshot = useGetStockSnapshot(entity)
  const transactions = useGetStocks(entity, filters, pagination, search, sorting) // prettier-ignore

  function refresh() {
    transactions.resolve()
  }

  return {
    entity,
    filters,
    pagination,
    snapshot,
    transactions,
    search,
    sorting,
    refresh,
  }
}
