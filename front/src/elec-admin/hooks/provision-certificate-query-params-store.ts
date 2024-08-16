import { Entity } from "carbure/types"
import { useLimit } from "common/components/pagination"
import { Order } from "common/components/table"
import useStore from "common/hooks/store"
import {
  ElecAdminProvisionCertificateFilterSelection,
  ElecAdminProvisionCertificateStates,
  ElecAdminProvisionCertificateStatus,
  ElecAdminSnapshot,
} from "elec-admin/types"
import { SafQueryType } from "saf/types"
import { useFilterSearchParams } from "./provision-certificate-filter-search-params"
import { CBQueryStates, CBSnapshot } from "common/hooks/query-builder"

export function useProvistionCertificateQueryParamsStore(
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
      search: undefined,
      order: undefined,
      selection: [],
      page: 0,
      limit,
    } as CBQueryStates,
    {
      setEntity: (entity: Entity) => ({
        entity,
        filters: filtersParams,
        selection: [],
        page: 0,
      }),

      setYear: (year: number) => ({
        year,
        filters: filtersParams,
        selection: [],
        page: 0,
      }),

      setSnapshot: (snapshot: CBSnapshot) => ({
        snapshot,
        filters: filtersParams,
        selection: [],
        page: 0,
      }),

      setStatus: (status: string) => {
        return {
          status,
          filters: filtersParams,
          selection: [],
          page: 0,
        }
      },

      setType: (type: SafQueryType) => {
        return {
          type,
          filters: filtersParams,
          selection: [],
          page: 0,
        }
      },

      setFilters: (filters: ElecAdminProvisionCertificateFilterSelection) => {
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
