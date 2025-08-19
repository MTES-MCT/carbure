import { useEffect, useMemo } from "react"
import useStore from "../store"
import {
  useFilterSearchParams,
  useLimit,
  usePage,
} from "./new-query-builder.hooks"
import {
  QueryBuilderActions,
  QueryBuilderStore,
  QueryBuilderStoreParams,
  QueryConfig,
  QueryParams,
  QueryTableOrder,
} from "./new-query-builder.types"
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
