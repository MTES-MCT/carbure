import { Entity } from "carbure/types"
import { useLimit } from "common/components/pagination"
import { Order } from "common/components/table"
import useStore from "common/hooks/store"
import useTitle from "common/hooks/title"
import { ElecAuditorApplicationsFilterSelection, ElecAuditorApplicationsSnapshot, ElecAuditorApplicationsStates, ElecAuditorApplicationsStatus } from "elec-auditor/types"
import { useTranslation } from "react-i18next"
import { useFilterSearchParams } from "./filter-search-params"


export function useApplicationsQueryParamsStore(
  entity: Entity,
  year: number,
  status: ElecAuditorApplicationsStatus,
  snapshot?: ElecAuditorApplicationsSnapshot,
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
      order: undefined,
      selection: [],
      page: 0,
      limit,
    } as ElecAuditorApplicationsStates,
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

      setSnapshot: (snapshot: ElecAuditorApplicationsSnapshot) => ({
        snapshot,
        filters: filtersParams,
        selection: [],
        page: 0,
      }),

      setStatus: (status: ElecAuditorApplicationsStatus) => {
        return {
          status,
          filters: filtersParams,
          selection: [],
          page: 0,
        }
      },

      setFilters: (filters: ElecAuditorApplicationsFilterSelection) => {
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

export function usePageTitle(state: ElecAuditorApplicationsStates) {
  const { t } = useTranslation()

  const title = "Points de recharge à auditer"
  const statuses: any = {
    [ElecAuditorApplicationsStatus.AuditInProgress]: t(title) + " " + t("en attente"),
    [ElecAuditorApplicationsStatus.AuditDone]: t(title) + " " + t("terminés"),
  }
  const entity = state.entity.name
  const year = state.year
  const status = statuses[state.status.toUpperCase()]

  useTitle(`${entity} ∙ ${status} ${year}`)
}