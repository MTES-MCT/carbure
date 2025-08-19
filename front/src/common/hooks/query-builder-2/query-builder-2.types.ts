import { ActionCreators } from "../store"

// Table component order
export interface QueryTableOrder {
  column: string
  direction: "asc" | "desc"
}

export type QueryStatus<
  T extends string | string[] | undefined = string | string[] | undefined,
> = {
  status?: T
}

export type QueryOrder<T extends string[] | undefined = string[] | undefined> =
  {
    order?: T
  }

export type QueryConfig<
  TStatus extends string | string[] | undefined = string | string[] | undefined,
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
export type QueryFilters = Record<string, string[]>
export type QueryFiltersManager = {
  filters: QueryFilters
  onFilter: (filters: QueryFilters) => void
}

// Params that can be passed to the query builder store
export type QueryBuilderStoreParams<
  S extends string | string[] | undefined = undefined,
> = {
  year?: number
  status?: S
}

// Data saved in the store
export type QueryBuilderStore<Config extends QueryConfig = QueryConfig> = {
  year?: number
  status?: Config["status"]
  filters: QueryFilters
  search?: string
  page: number
  limit?: number
  order?: QueryTableOrder
  selection: number[]
}

export type QueryBuilderActions<Config extends QueryConfig = QueryConfig> = {
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
  TStatus extends string | string[] | undefined,
  TOrder extends string[] | undefined = undefined,
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
