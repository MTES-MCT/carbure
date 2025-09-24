/**
 * Query Builder Hook (Refactored)
 *
 * This hook provides a generic and type-safe way to manage query parameters for paginated, filterable, and sortable lists.
 * It is designed to be used with API endpoints that accept parameters such as page, limit, filters, and order.
 *
 * Usage Overview:
 * 1. Define a QueryBuilder type with the appropriate generics for your use case (e.g. status, order).
 * 2. Use this builder to type your query object for the backend (using Builder["query"]).
 * 3. When using the hook, pass the generic typing via Builder["config"].
 *
 * Example (see accounting/types.ts):
 *
 *   // 1. Define the builder type for your resource
 *   export type OperationsQueryBuilder = QueryBuilder<
 *     OperationsStatus[],
 *     OperationOrder[]
 *   >
 *
 *   // 2. Type your query object for the backend
 *   export type OperationsQuery = OperationsQueryBuilder["query"]
 *
 *   // 3. Use the hook in your component
 *   const { query, state, actions } = useQueryBuilder<OperationsQueryBuilder["config"]>()
 *
 *   // 'query' is correctly typed and can be sent to the backend
 *   // 'state' and 'actions' allow you to manage pagination, filters, order, etc.
 *
 * This approach ensures type safety and consistency between frontend and backend query parameters.
 *
 * See also: accounting/types.ts for concrete usage examples.
 */
import { useEffect, useMemo } from "react"
import useStore from "../store"
import {
  useFilterSearchParams,
  useLimit,
  usePage,
} from "./query-builder-2.hooks"
import {
  QueryBuilderActions,
  QueryBuilderStore,
  QueryBuilderStoreParams,
  QueryConfig,
  QueryParams,
  QueryTableOrder,
} from "./query-builder-2.types"
import useEntity from "../entity"

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

export const QUERY_RESET = {
  limit: undefined,
  page: 1,
  order_by: undefined,
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

const currentYear = new Date().getFullYear()

export function useQueryBuilder<Config extends QueryConfig>(
  params?: QueryBuilderStoreParams<Config["status"]>
) {
  const [state, actions] = useQueryBuilderStore<Config>(params)
  const entity = useEntity()
  const { year, status, page = 1, limit, filters, order, search } = state

  const query = useMemo<QueryParams<Config>>(
    () => ({
      entity_id: entity.id,
      year: year ?? currentYear,
      status,
      page: page > 0 ? page : 1,
      page_size: limit ?? undefined,
      order_by: order ? formatOrder<Config["order"]>(order) : undefined,
      search,
      ...filters,
    }),
    [entity.id, status, limit, filters, page, year, order, search]
  )

  return { query, state, actions } as const
}
