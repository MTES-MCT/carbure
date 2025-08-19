import { useEffect, useMemo } from "react"
import { useSearchParams } from "react-router-dom"
import useLocalStorage from "./storage"
import useStore, { ActionCreators } from "./store"
import useEntity from "./entity"

// VERSION QUI OBLIGE DE DÉFINIR UN TYPAGE GENERIQUE POUR status et order
export interface QueryTableOrder {
  column: string
  direction: "asc" | "desc"
}

export type QueryStatus<T extends string | undefined = string | undefined> = {
  status?: T
}

export type QueryOrder<T extends string[] | undefined = string[] | undefined> =
  {
    order?: T
  }

export type QueryConfig<
  TStatus extends string | undefined = string | undefined,
  TOrder extends string[] | undefined = string[] | undefined,
> = QueryStatus<TStatus> & QueryOrder<TOrder>

// Final query params to be used in the API call
export type QueryParams<Q extends QueryConfig> = {
  entity_id: number
  year: number
  status?: Q["status"]
  search?: string
  page: number
  limit?: number
  order_by?: Q["order"]
}

// Filters are defined by a key and a value array of strings
type QueryFilters = Record<string, string[]>

// Params that can be passed to the query builder store
type QueryBuilderStoreParams<S extends string | undefined = undefined> = {
  year?: number
  status?: S
}

// Data saved in the store
type QueryBuilderStore<Config extends QueryConfig = QueryConfig> = {
  year?: number
  status?: Config["status"]
  filters: QueryFilters
  search?: string
  page: number
  limit?: number
  order?: QueryTableOrder
  selection: number[]
}

type QueryBuilderActions<Config extends QueryConfig = QueryConfig> = {
  setYear: (year: number) => Partial<QueryBuilderStore<Config>>
  setStatus: (status: Config["status"]) => Partial<QueryBuilderStore<Config>>
  setFilters: (filters: QueryFilters) => Partial<QueryBuilderStore<Config>>
  setOrder: (
    order: QueryTableOrder | undefined
  ) => Partial<QueryBuilderStore<Config>>
  setPage: (page?: number) => Partial<QueryBuilderStore<Config>>
  setLimit: (limit?: number) => Partial<QueryBuilderStore<Config>>
  setSearch: (search: string | undefined) => Partial<QueryBuilderStore<Config>>
  setSelection: (selection: number[]) => Partial<QueryBuilderStore<Config>>
}

// Type that exposes all the types related to the query builder
export type QueryBuilder<
  TStatus extends string | undefined,
  TOrder extends string[] | undefined,
> = {
  // State of the store
  state: QueryBuilderStore<QueryConfig<TStatus, TOrder>>

  // Actions to update the store
  actions: ActionCreators<
    QueryBuilderStore<QueryConfig<TStatus, TOrder>>,
    QueryBuilderActions<QueryConfig<TStatus, TOrder>>
  >

  // Final query sent to the backend
  query: QueryParams<QueryConfig<TStatus, TOrder>>

  // Config required to the useQueryBuilder to pass generic types
  config: QueryConfig<TStatus, TOrder>
}

const useFilterSearchParams = () => {
  const [filtersParams, setFiltersParams] = useSearchParams()
  const filters = useMemo(() => {
    const filters: QueryFilters = {}
    filtersParams.forEach((value, filter) => {
      filters[filter] = filters[filter] ?? []
      filters[filter]!.push(value)
    })
    return filters
  }, [filtersParams])

  return [filters, setFiltersParams] as const
}

/**
 * Define the number of items per page
 */
export const useLimit = () => {
  return useLocalStorage<number | undefined>("carbure:limit", 10)
}

const usePage = () => {
  const [searchParams] = useSearchParams()
  const searchParamsPage = searchParams.get("page")

  return searchParamsPage ? parseInt(searchParamsPage) : 1
}

const currentYear = new Date().getFullYear()

const formatOrder = <Columns extends string[] | undefined>(
  order: QueryTableOrder | undefined
): Columns => {
  if (!order) return [] as unknown as Columns
  const mapping = {
    asc: order.column,
    desc: `-${order.column}`,
  }

  return [mapping[order.direction]] as Columns
}

export const useQueryBuilderStore = <Config extends QueryConfig = QueryConfig>(
  params: QueryBuilderStoreParams<Config["status"]> = {}
) => {
  const [limit, saveLimit] = useLimit()
  const [filtersParams, setFiltersParams] = useFilterSearchParams()
  // Retrieve page from url and set the "page" attribute in the store
  const page = usePage()

  const [state, actions] = useStore<
    QueryBuilderStore<Config>,
    QueryBuilderActions<Config>
  >(
    {
      year: params.year,
      status: params.status,
      filters: filtersParams,
      page,
      limit,
      order: undefined,
      selection: [],
    },
    {
      setYear: (year) => ({
        year,
        filters: filtersParams,
        page: 1,
      }),

      setStatus: (status) => {
        return {
          status,
          filters: filtersParams,
          page: 1,
        }
      },

      setFilters: (filters) => {
        setTimeout(() => {
          setFiltersParams(filters)
        })
        return {
          filters,
          page: 1,
        }
      },

      setOrder: (order) => ({
        order,
      }),

      setPage: (page) => ({
        page,
      }),

      setLimit: (limit) => {
        saveLimit(limit)
        return {
          limit,
          page: 1,
        }
      },

      setSearch: (search) => ({
        search,
        page: 1,
      }),

      setSelection: (selection: number[]) => ({
        selection,
      }),
    }
  )

  // If an external component updates page query, we need to sync the store with the new value
  useEffect(() => {
    actions.setPage(page)
  }, [page, actions])

  // sync store state with status set in the route
  if (params.status && state.status !== params.status) {
    actions.setStatus?.(params.status)
  }

  // sync store state with year set from above
  if (params.year && state.year !== params.year) {
    actions.setYear(params.year)
  }

  return [state, actions] as const
}

export function useQueryBuilder<Config extends QueryConfig>(
  params: QueryBuilderStoreParams<Config["status"]>
) {
  const [state, actions] = useQueryBuilderStore<Config>(params)
  const entity = useEntity()
  const { year, status, page = 1, limit, filters, order } = state

  const query = useMemo<QueryParams<Config>>(
    () => ({
      entity_id: entity.id,
      year: year ?? currentYear,
      status,
      page: page > 0 ? page : 1,
      page_size: limit ?? undefined,
      order_by: order ? formatOrder<Config["order"]>(order) : undefined,
      ...filters,
    }),
    [entity.id, status, limit, filters, page, year, order]
  )

  return { query, state, actions } as const
}
