import { Entity } from "carbure/types"
import { useLimit } from "common/components/pagination"
import useStore from "common/hooks/store"
import { SafFilterSelection, SafOperatorSnapshot, SafStates, SafTicketSourceStatus } from "saf/types"
import { useFilterSearchParams } from "./filter-search-params"

export function useQueryParamsStore(
  entity: Entity,
  year: number,
  status: string | undefined,
  snapshot?: SafOperatorSnapshot | undefined
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
      search: undefined,
      invalid: false,
      deadline: false,
      order: undefined,
      selection: [],
      page: 0,
      limit,
    } as SafStates,
    {
      setEntity: (entity: Entity) => (state) => ({
        entity,
        filters: filtersParams,
        invalid: false,
        deadline: false,
        selection: [],
        page: 0,
      }),

      setYear: (year: number) => (state) => ({
        year,
        filters: filtersParams,
        invalid: false,
        deadline: false,
        selection: [],
        page: 0,
      }),

      setSnapshot: (snapshot: SafOperatorSnapshot) => (state) => {
        return {
          snapshot,
          filters: filtersParams,
          invalid: false,
          deadline: false,
          selection: [],
          page: 0,
        }
      },

      setStatus: (status: SafTicketSourceStatus) => (state) => ({
        status,
        filters: filtersParams,
        invalid: false,
        deadline: false,
        selection: [],
        page: 0,
      }),

      setFilters: (filters: SafFilterSelection) => {
        setTimeout(() => {
          setFiltersParams(filters)
        })
        return {
          filters,
          selection: [],
          page: 0,
        }
      },

      // setSearch: (search: string | undefined) => ({
      //   search,
      //   selection: [],
      //   page: 0,
      // }),

      // setInvalid: (invalid: boolean) => ({
      //   invalid,
      //   selection: [],
      //   page: 0,
      // }),

      // setDeadline: (deadline: boolean) => ({
      //   deadline,
      //   selection: [],
      //   page: 0,
      // }),

      // setOrder: (order: Order | undefined) => ({
      //   order,
      // }),

      // setSelection: (selection: number[]) => ({
      //   selection,
      // }),

      // setPage: (page?: number) => ({
      //   page,
      //   selection: [],
      // }),

      // setLimit: (limit?: number) => {
      //   saveLimit(limit)
      //   return {
      //     limit,
      //     selection: [],
      //     page: 0,
      //   }
      // },
    }
  )

  // sync tab title with current state
  // useLotTitle(state)

  // sync store state with entity set from above
  if (state.entity.id !== entity.id) {
    actions.setEntity(entity)
  }

  // sync store state with year set from above
  if (state.year !== year) {
    actions.setYear(year)
  }

  // sync store state with status set in the route
  if (state.status !== status) {
    actions.setStatus(status as SafTicketSourceStatus)
  }

  if (snapshot && state.snapshot !== snapshot) {
    actions.setSnapshot(snapshot)
  }

  return [state, actions] as [typeof state, typeof actions]
}