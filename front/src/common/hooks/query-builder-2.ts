import { Entity } from "carbure/types"
import { useLimit } from "common/components/pagination"
import { Order } from "common/components/table"
import { useEffect, useMemo } from "react"
import useStore from "./store"
import { useSearchParams } from "react-router-dom"

type OrderColumns<Columns extends string[]> = {
  [K in keyof Columns]: Columns[K] extends string
    ? Columns[K]
    : `-${Columns[K]}`
}

export type CBSnapshot = Record<string, number>

export type CBFilterSelection = Record<string, string[]>

export const CBQUERY_RESET: Partial<CBQueryParams<[]>> = {
  limit: undefined,
  page: 1,
  order: undefined,
}

const formatOrder = <Columns extends string[]>(
  order: Order | undefined
): Columns => {
  if (!order) return [] as unknown as Columns
  const mapping = {
    asc: order.column,
    desc: `-${order.column}`,
  }

  return [mapping[order.direction]] as Columns
}

interface BaseCBQueryStates {
  entity: Entity
  year: number
  filters: CBFilterSelection
  search?: string
  status: string
  type?: string // Extra info used when we have to call the same endpoint for two different views (See saf operator page)
  selection: number[]
  page: number
  limit?: number
  order?: Order
}
export type CBQueryStates<
  GenericCBQueryStates extends BaseCBQueryStates = BaseCBQueryStates,
> = {
  entity: GenericCBQueryStates["entity"]
  year: GenericCBQueryStates["year"]
  filters: GenericCBQueryStates["filters"]
  search?: GenericCBQueryStates["search"]
  status: GenericCBQueryStates["status"]
  type?: GenericCBQueryStates["type"]
  page: GenericCBQueryStates["page"]
  selection: GenericCBQueryStates["selection"]
  limit?: GenericCBQueryStates["limit"]
  order?: GenericCBQueryStates["order"]
}
export interface CBQueryParams<Columns extends string[]> {
  entity_id: number
  year: number
  status: string
  type?: string
  search?: string
  page: number
  limit?: number
  order?: OrderColumns<Columns>
}

/* Hooks */

export function useCBQueryBuilder<Columns extends string[]>(
  params: CBQueryStates
): CBQueryParams<Columns> {
  const {
    entity,
    year,
    status,
    type,
    search,
    page = 1,
    limit,
    order,
    filters,
  } = params

  return useMemo<CBQueryParams<Columns>>(
    () => ({
      entity_id: entity.id,
      year,
      status,
      type,
      search,
      page: page > 0 ? page : 1,
      page_size: limit ?? undefined,
      order: formatOrder<OrderColumns<Columns>>(order),
      ...filters,
    }),
    [entity.id, status, type, search, limit, order, filters, page, year]
  )
}

export function useCBQueryParamsStore<
  GenericCBQueryStates extends BaseCBQueryStates = BaseCBQueryStates,
>(entity: Entity, year: number, status: string, type?: string) {
  const [limit, saveLimit] = useLimit()
  const [{ page, ...filtersParams }, setFiltersParams] = useFilterSearchParams()

  // Retrieve page from url and set the "page" attribute in the store
  const computedPage = page?.[0] ? parseInt(page[0]) : 1

  const [state, actions] = useStore(
    {
      entity,
      year,
      status,
      type,
      filters: filtersParams,
      order: undefined,
      selection: [],
      page: computedPage,
      limit,
    } as CBQueryStates<GenericCBQueryStates>,
    {
      setEntity: (entity: Entity) => ({
        entity,
        filters: filtersParams,
        selection: [],
        page: 1,
      }),

      setYear: (year: number) => ({
        year,
        filters: filtersParams,
        selection: [],
        page: 1,
      }),

      setStatus: (status: string) => {
        return {
          status,
          filters: filtersParams,
          selection: [],
          page: 1,
        }
      },

      setType: (type: string) => {
        return {
          type,
          filters: filtersParams,
          selection: [],
          page: 1,
        }
      },

      setFilters: (filters: CBFilterSelection) => {
        setTimeout(() => {
          setFiltersParams(filters)
        })
        return {
          filters,
          selection: [],
          page: 1,
        }
      },

      setSearch: (search: string | undefined) => ({
        search,
        selection: [],
        page: 1,
      }),

      setOrder: (order: Order | undefined) => ({
        order,
      }),

      setSelection: (selection: number[]) => ({
        selection,
      }),

      setPage: (page?: number) => {
        return {
          page,
          selection: [],
        }
      },

      setLimit: (limit?: number) => {
        saveLimit(limit)
        return {
          limit,
          selection: [],
          page: 1,
        }
      },
    }
  )

  // If an external component updates page query, we need to sync the store with the new value
  useEffect(() => {
    const currentPage = parseInt(page?.[0] ?? "1")

    actions.setPage(currentPage)
  }, [page, actions])

  // sync store state with entity set from above
  if (state.entity.id !== entity.id) {
    actions.setEntity(entity)
  }

  // sync store state with year set from above
  if (state.year !== year) {
    actions.setYear(year)
  }

  // // sync store state with status set in the route
  if (state.status !== status) {
    actions.setStatus(status)
  }

  if (type && state.type !== type) {
    actions.setType(type)
  }

  return [state, actions] as [typeof state, typeof actions]
}

function useFilterSearchParams() {
  const [filtersParams, setFiltersParams] = useSearchParams()
  const filters = useMemo(() => {
    const filters: CBFilterSelection = {}
    filtersParams.forEach((value, filter) => {
      const fkey = filter as string
      filters[fkey] = filters[fkey] ?? []
      filters[fkey]!.push(value)
    })
    return filters
  }, [filtersParams])
  return [filters, setFiltersParams] as [typeof filters, typeof setFiltersParams] // prettier-ignore
}
