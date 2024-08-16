import { Entity } from "carbure/types"
import { useLimit } from "common/components/pagination"
import { Order } from "common/components/table"
import { ElecAdminProvisionCertificateFilter } from "elec-admin/types"
import { useMemo } from "react"
import useStore from "./store"
import { useSearchParams } from "react-router-dom"


/* Types */
export type CBSnapshot = Record<string, number>

export type CBFilterSelection = Record<string, string[]>

export const CBQUERY_RESET: Partial<CBQueryParams> = {
  limit: undefined,
  from_idx: undefined,
  sort_by: undefined,
  order: undefined,
}
export interface CBQueryStates {
  entity: Entity
  year: number
  filters: CBFilterSelection
  search?: string
  status: string
  selection: number[]
  page: number
  limit?: number
  order?: Order
  snapshot?: CBSnapshot
}

export interface CBQueryParams {
  entity_id: number;
  year: number;
  status: string;
  search?: string;
  from_idx: number;
  limit?: number;
  sort_by?: string;
  order?: 'asc' | 'desc';
}


/* Hooks */

export function useCBQueryBuilder(params: CBQueryStates): CBQueryParams {
  const {
    entity,
    year,
    status,
    search,
    page = 0,
    limit,
    order,
    filters,
  } = params;

  return useMemo<CBQueryParams>(
    () => ({
      entity_id: entity.id,
      year,
      status,
      search,
      from_idx: page * (limit ?? 0),
      limit: limit || undefined,
      sort_by: order?.column,
      order: order?.direction,
      ...filters,
    } as CBQueryParams),
    [entity.id, status, search, limit, order, filters, page, year]
  )
}





export function useCBQueryParamsStore(
  entity: Entity,
  year: number,
  status: string,
  snapshot?: CBSnapshot,
  onUpdatePageTitle?: (state: CBQueryStates) => void
) {
  const [limit, saveLimit] = useLimit()
  const [filtersParams, setFiltersParams] = useFilterSearchParams()

  const [state, actions] = useStore(
    {
      entity,
      year,
      snapshot,
      status,
      filters: filtersParams,
      // search: undefined,
      // invalid: false,
      // deadline: false,
      order: undefined,
      selection: [],
      page: 0,
      limit,
    } as CBQueryStates,
    {
      setEntity: (entity: Entity) => ({
        entity,
        filters: filtersParams,
        // invalid: false,
        // deadline: false,
        selection: [],
        page: 0,
      }),

      setYear: (year: number) => ({
        year,
        filters: filtersParams,
        // invalid: false,
        // deadline: false,
        selection: [],
        page: 0,
      }),

      setSnapshot: (snapshot: CBSnapshot) => ({
        snapshot,
        filters: filtersParams,
        // invalid: false,
        // deadline: false,
        selection: [],
        page: 0,
      }),

      setStatus: (status: string) => {
        return {
          status,
          filters: filtersParams,
          // invalid: false,
          // deadline: false,
          selection: [],
          page: 0,
        }
      },

      // setType: (type: ElecCPOQ) => {
      //   return {
      //     type,
      //     filters: filtersParams,
      //     selection: [],
      //     page: 0,
      //   }
      // },

      setFilters: (filters: CBFilterSelection) => {
        setTimeout(() => {
          setFiltersParams(filters)
        })
        return {
          filters,
          selection: [],
          page: 0,
        }
      },

      setSearch: (search: string | undefined) => ({
        search,
        selection: [],
        page: 0,
      }),

      setOrder: (order: Order | undefined) => ({
        order,
      }),

      setSelection: (selection: number[]) => ({
        selection,
      }),

      setPage: (page?: number) => ({
        page,
        selection: [],
      }),

      setLimit: (limit?: number) => {
        saveLimit(limit)
        return {
          limit,
          selection: [],
          page: 0,
        }
      },
    }
  )

  // sync tab title with current state
  onUpdatePageTitle && onUpdatePageTitle(state)

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

  if (snapshot && state.snapshot !== snapshot) {
    actions.setSnapshot(snapshot)
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
