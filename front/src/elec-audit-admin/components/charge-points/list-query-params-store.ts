import { Entity } from "carbure/types"
import { useLimit } from "common/components/pagination"
import { Order } from "common/components/table"
import useStore from "common/hooks/store"
import useTitle from "common/hooks/title"
import { ElecAdminAuditFilterSelection, ElecAdminAuditSnapshot, ElecAdminAuditStates, ElecAdminAuditStatus } from "elec-audit-admin/types"
import { useTranslation } from "react-i18next"
import { useFilterSearchParams } from "../../../elec-admin/hooks/provision-certificate-filter-search-params"

export function useElecAdminAuditChargePointsQueryParamsStore(
  entity: Entity,
  year: number,
  status: ElecAdminAuditStatus,
  snapshot?: ElecAdminAuditSnapshot,
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
    } as ElecAdminAuditStates,
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

      setSnapshot: (snapshot: ElecAdminAuditSnapshot) => ({
        snapshot,
        filters: filtersParams,
        // invalid: false,
        // deadline: false,
        selection: [],
        page: 0,
      }),

      setStatus: (status: ElecAdminAuditStatus) => {
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

      setFilters: (filters: ElecAdminAuditFilterSelection) => {
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
  usePageTitle(state)

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

export function usePageTitle(state: ElecAdminAuditStates) {
  const { t } = useTranslation()

  const title = "Inscriptions des points de recharge"
  const statuses: any = {
    [ElecAdminAuditStatus.Pending]: t(title) + " " + t("en attente"),
    [ElecAdminAuditStatus.History]: t(title) + " " + t("historique"),
  }
  const entity = state.entity.name
  const year = state.year
  const status = statuses[state.status.toUpperCase()]

  useTitle(`${entity} ∙ ${status} ${year}`)
}