import { Entity } from "common/types"
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

export type CBQueryFilterManager = {
  filters: CBFilterSelection
  onFilter: (filters: CBFilterSelection) => void
}

export const CBQUERY_RESET: Partial<CBQueryParams<[], undefined, undefined>> = {
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

export type CBQueryStates<S, T> = {
  entity: Entity
  year: number
  filters: CBFilterSelection
  search?: string
  status?: S
  type?: T // Extra info used when we have to call the same endpoint for two different views (See saf operator page)
  selection: number[]
  page: number
  limit?: number
  order?: Order
}
export interface CBQueryParams<Columns extends string[], Status, Type> {
  entity_id: number
  year: number
  status?: Status
  type?: Type
  search?: string
  page: number
  limit?: number
  order?: OrderColumns<Columns>
}

/* Hooks */
export function useCBQueryBuilder<Columns extends string[], Status, Type>(
  params: CBQueryStates<Status, Type>
): CBQueryParams<Columns, Status, Type> {
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

  return useMemo<CBQueryParams<Columns, Status, Type>>(
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

export function useCBQueryParamsStore<S, T>(
  entity: Entity,
  year?: number,
  status?: S,
  type?: T
) {
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
    } as CBQueryStates<S, T>,
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

      setStatus: (status: S) => {
        return {
          status,
          filters: filtersParams,
          selection: [],
          page: 1,
        }
      },

      setType: (type: T) => {
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
  if (year && state.year !== year) {
    actions.setYear(year)
  }

  // // sync store state with status set in the route
  if (status && state.status !== status) {
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
