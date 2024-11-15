import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { useLocation, Navigate } from "react-router-dom"
import * as api from "../../api"
import { Entity, UserRole } from "carbure/types"
import {
  Lot,
  Snapshot,
  FilterSelection,
  Status,
  LotQuery,
  Filter,
} from "../../types"
import useEntity from "carbure/hooks/entity"
import { useAutoStatus } from "../status"
import { useQuery } from "common/hooks/async"
import { Order } from "common/components/table"
import { Bar } from "common/components/scaffold"
import Pagination, { useLimit } from "common/components/pagination"
import Filters, { useFilterParams } from "../filters"
import LotTable from "./lot-table"
import NoResult from "../../../common/components/no-result"
import LotActions from "./lot-actions"
import { DeadlineSwitch, InvalidSwitch } from "../switches"
import { LotSummaryBar } from "./lot-summary"
import SearchBar from "../search-bar"
import LotAdd from "lot-add"
import LotDetails from "transaction-details/components/lots"
import useStore from "common/hooks/store"
import { useMatomo } from "matomo"
import { getDefaultCategory, useAutoCategory } from "../category"
import useTitle from "common/hooks/title"
import { AdminStatus } from "controls/types"
import HashRoute from "common/components/hash-route"

export interface LotsProps {
  year: number
  snapshot: Snapshot | undefined
}

export const Lots = ({ year, snapshot }: LotsProps) => {
  const matomo = useMatomo()
  const location = useLocation()

  const entity = useEntity()
  const status = useAutoStatus()
  const category = useAutoCategory(status, snapshot)

  const [state, actions] = useQueryParamsStore(entity, year, status, category, snapshot) // prettier-ignore
  const query = useLotQuery(state)

  const lots = useQuery(api.getLots, {
    key: "lots",
    params: [query],

    onSuccess: () => {
      if (state.selection.length > 0) {
        actions.setSelection([])
      }
    },
  })

  const lotsData = lots.result?.data
  const lotList = lotsData?.results ?? []
  const ids = lotsData?.ids ?? []
  const lotErrors = lotsData?.errors ?? {}
  const count = lotsData?.results.length ?? 0
  const total = lotsData?.count ?? 0
  const totalErrors = lotsData?.total_errors ?? 0
  const totalDeadline = lotsData?.total_deadline ?? 0


  const trackShowLotDetails = (lot: Lot) => {
    matomo.push(["trackEvent", "lots-details", "show-lot-details", lot.id])
  }

  const showLotDetails = (lot: Lot) => ({
    pathname: location.pathname,
    search: location.search,
    hash: `lot/${lot.id}`,
  })

  if (category === undefined) {
    const defaultCategory = getDefaultCategory(status, snapshot)
    return <Navigate to={`${status}/${defaultCategory}`} />
  }

  return (
    <>
      <Bar>
        <Filters
          query={query}
          filters={filtersByStatus[status]}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilters={api.getLotFilters}
        />
      </Bar>

      <section>
        <SearchBar
          count={snapshot?.lots}
          search={state.search}
          category={state.category}
          query={query}
          selection={state.selection}
          onSearch={actions.setSearch}
          onSwitch={actions.setCategory}
        />

        {entity.hasRights(UserRole.Admin, UserRole.ReadWrite) && (
          <LotActions
            count={count}
            category={state.category}
            query={query}
            selection={state.selection}
          />
        )}

        {(state.invalid || totalErrors > 0) && (
          <InvalidSwitch
            count={totalErrors}
            active={state.invalid}
            onSwitch={actions.setInvalid}
          />
        )}

        {(state.deadline || totalDeadline > 0) && (
          <DeadlineSwitch
            count={totalDeadline}
            active={state.deadline}
            onSwitch={actions.setDeadline}
          />
        )}

        {count === 0 && (
          <NoResult
            loading={lots.loading}
            filters={state.filters}
            onFilter={actions.setFilters}
          />
        )}

        {count > 0 && (
          <>
            <LotSummaryBar
              query={query}
              selection={state.selection}
              filters={state.filters}
              onFilter={actions.setFilters}
            />

            <LotTable
              loading={lots.loading}
              order={state.order}
              lots={lotList}
              errors={lotErrors}
              selected={state.selection}
              rowLink={showLotDetails}
              onSelect={actions.setSelection}
              onAction={trackShowLotDetails}
              onOrder={actions.setOrder}
            />

            <Pagination
              page={state.page}
              limit={state.limit}
              total={total}
              onPage={actions.setPage}
              onLimit={actions.setLimit}
            />
          </>
        )}
      </section>

      <HashRoute path="add" element={<LotAdd />} />
      <HashRoute path="lot/:id" element={<LotDetails neighbors={ids} />} />
    </>
  )
}

const DRAFT_FILTERS = [
  Filter.Periods,
  Filter.Biofuels,
  Filter.Feedstocks,
  Filter.CountriesOfOrigin,
  Filter.Suppliers,
  Filter.Clients,
  Filter.ProductionSites,
  Filter.DeliverySites,
  Filter.Scores,
]

const IN_FILTERS = [
  Filter.LotStatus,
  Filter.DeliveryTypes,
  Filter.Periods,
  Filter.Biofuels,
  Filter.Feedstocks,
  Filter.CountriesOfOrigin,
  Filter.Suppliers,
  Filter.ProductionSites,
  Filter.DeliverySites,
  Filter.Scores,
]

const OUT_FILTERS = [
  Filter.LotStatus,
  Filter.Periods,
  Filter.Biofuels,
  Filter.Feedstocks,
  Filter.CountriesOfOrigin,
  Filter.Clients,
  Filter.ClientTypes,
  Filter.ProductionSites,
  Filter.DeliverySites,
  Filter.Scores,
]

const filtersByStatus: Record<Status, Filter[]> = {
  drafts: DRAFT_FILTERS,
  in: IN_FILTERS,
  out: OUT_FILTERS,
  stocks: [],
  declaration: [],
  unknown: [],
}

export interface QueryParams {
  entity: Entity
  year: number
  status: Status
  category: string
  filters: FilterSelection
  search: string | undefined
  invalid: boolean
  deadline: boolean
  selection: number[]
  page: number
  limit: number | undefined
  order: Order | undefined
  snapshot: Snapshot | undefined
}

export function useQueryParamsStore(
  entity: Entity,
  year: number,
  status: string,
  category?: string,
  snapshot?: Snapshot | undefined
) {
  const [limit, saveLimit] = useLimit()
  const [filtersParams, setFiltersParams] = useFilterParams()

  const [state, actions] = useStore(
    {
      entity,
      year,
      snapshot,
      status,
      category: getDefaultCategory(status, snapshot),
      filters: filtersParams,
      search: undefined,
      invalid: false,
      deadline: false,
      order: undefined,
      selection: [],
      page: 0,
      limit,
    } as QueryParams,
    {
      setEntity: (entity: Entity) => (state) => ({
        entity,
        category: getDefaultCategory(state.status, state.snapshot),
        filters: filtersParams,
        invalid: false,
        deadline: false,
        selection: [],
        page: 0,
      }),

      setYear: (year: number) => (state) => ({
        year,
        category: getDefaultCategory(state.status, state.snapshot),
        filters: filtersParams,
        invalid: false,
        deadline: false,
        selection: [],
        page: 0,
      }),

      setSnapshot: (snapshot: Snapshot) => (state) => ({
        snapshot,
        category: getDefaultCategory(state.status, snapshot),
        filters: filtersParams,
        invalid: false,
        deadline: false,
        selection: [],
        page: 0,
      }),

      setStatus: (status: Status) => (state) => ({
        status,
        category: getDefaultCategory(status, state.snapshot),
        filters: filtersParams,
        invalid: false,
        deadline: false,
        selection: [],
        page: 0,
      }),

      setCategory: (category: string) => ({
        category,
        filters: filtersParams,
        invalid: false,
        deadline: false,
        selection: [],
        page: 0,
      }),

      setFilters: (filters: FilterSelection) => {
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

      setInvalid: (invalid: boolean) => ({
        invalid,
        selection: [],
        page: 0,
      }),

      setDeadline: (deadline: boolean) => ({
        deadline,
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
  useLotTitle(state)

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
    actions.setStatus(status as Status)
  }

  // sync store state with category set in the route
  if (category && state.category !== category) {
    actions.setCategory(category)
  }

  if (snapshot && state.snapshot !== snapshot) {
    actions.setSnapshot(snapshot)
  }

  return [state, actions] as [typeof state, typeof actions]
}

export function useLotTitle(state: QueryParams) {
  const { t } = useTranslation()

  const statuses: Record<Status, string> = {
    drafts: t("brouillons"),
    in: t("lots reçus"),
    out: t("lots envoyés"),
    stocks: t("stocks"),
    declaration: "",
    unknown: "",
  }

  const adminStatuses: Record<AdminStatus, string> = {
    alerts: t("alertes"),
    lots: t("lots"),
    stocks: t("stocks"),
    unknown: "",
  }

  const categories: any = {
    pending: t("en attente"),
    correction: t("en correction"),
    history: "",
  }

  const entity = state.entity.name
  const year = state.year
  const status =
    state.status in statuses
      ? statuses[state.status]
      : (adminStatuses[state.status as AdminStatus] ?? "")
  const category = state.status in statuses ? categories[state.category] : ""

  useTitle(`${entity} ∙ ${status} ${category} ${year}`)
}

export function useLotQuery({
  entity,
  status,
  category,
  year,
  search,
  invalid,
  deadline,
  page = 0,
  limit,
  order,
  filters,
}: QueryParams) {
  return useMemo<LotQuery>(
    () => ({
      entity_id: entity.id,
      year,
      status: status.toUpperCase(),
      category,
      query: search ? search : undefined,
      history: category === "history" ? true : undefined,
      correction: category === "correction" ? true : undefined,
      invalid: invalid ? true : undefined,
      deadline: deadline ? true : undefined,
      from_idx: page * (limit ?? 0),
      limit: limit || undefined,
      sort_by: order?.column,
      order: order?.direction,
      ...filters,
    }),
    [
      entity.id,
      year,
      status,
      category,
      search,
      invalid,
      limit,
      order,
      filters,
      deadline,
      page,
    ]
  )
}

export default Lots
