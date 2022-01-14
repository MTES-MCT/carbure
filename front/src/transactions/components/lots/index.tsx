import { useMemo } from "react"
import { Route, Routes, useNavigate, useLocation } from "react-router-dom"
import * as api from "../../api"
import { Entity } from "carbure/types"
import {
  Lot,
  Snapshot,
  FilterSelection,
  Status,
  LotQuery,
  Filter,
} from "../../types"
import { useStatus } from "../status"
import { useQuery } from "common-v2/hooks/async"
import { Order } from "common-v2/components/table"
import { Bar } from "common-v2/components/scaffold"
import Pagination, { useLimit } from "common-v2/components/pagination"
import Filters, { useFilterParams } from "../filters"
import { LotTable } from "./lot-table"
import NoResult from "../no-result"
import { LotActions } from "./lot-actions"
import { DeadlineSwitch, InvalidSwitch } from "../switches"
import { LotSummaryBar } from "./lot-summary"
import SearchBar from "../search-bar"
import LotAdd from "lot-add"
import LotDetails from "lot-details"
import useStore from "common-v2/hooks/store"
import { useMatomo } from "matomo"

export interface LotsProps {
  entity: Entity
  year: number
  snapshot: Snapshot | undefined
}

export const Lots = ({ entity, year, snapshot }: LotsProps) => {
  const matomo = useMatomo()
  const location = useLocation()
  const navigate = useNavigate()

  const status = useStatus()

  const [state, actions] = useQueryParamsStore(entity, year, status, snapshot)
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

  const lotsData = lots.result?.data.data
  const lotList = lotsData?.lots ?? []
  const ids = lotsData?.ids ?? []
  const lotErrors = lotsData?.errors ?? {}
  const count = lotsData?.returned ?? 0
  const total = lotsData?.total ?? 0
  const totalErrors = lotsData?.total_errors ?? 0
  const totalDeadline = lotsData?.total_deadline ?? 0

  const showLotDetails = (lot: Lot) => {
    matomo.push(["trackEvent", "lots-details", "show-lot-details"])
    navigate({
      pathname: `${status}/${lot.id}`,
      search: location.search,
    })
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
          onSearch={actions.setSearch}
          onSwitch={actions.setCategory}
        />

        <LotActions
          count={count}
          category={state.category}
          query={query}
          selection={state.selection} //
        />

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
              onSelect={actions.setSelection}
              onAction={showLotDetails}
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

      <Routes>
        <Route path="drafts/add" element={<LotAdd />} />
        <Route path=":status/:id" element={<LotDetails neighbors={ids} />} />
      </Routes>
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
]

const IN_FILTERS = [
  Filter.Periods,
  Filter.Biofuels,
  Filter.Feedstocks,
  Filter.CountriesOfOrigin,
  Filter.Suppliers,
  Filter.ProductionSites,
  Filter.DeliverySites,
]

const OUT_FILTERS = [
  Filter.Periods,
  Filter.Biofuels,
  Filter.Feedstocks,
  Filter.CountriesOfOrigin,
  Filter.Clients,
  Filter.ProductionSites,
  Filter.DeliverySites,
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
        search: undefined,
        invalid: false,
        deadline: false,
        selection: [],
        page: 0,
      }),

      setYear: (year: number) => (state) => ({
        year,
        category: getDefaultCategory(state.status, state.snapshot),
        filters: filtersParams,
        search: undefined,
        invalid: false,
        deadline: false,
        selection: [],
        page: 0,
      }),

      setSnapshot: (snapshot: Snapshot | undefined) => (state) => {
        return {
          snapshot,
          category: getDefaultCategory(state.status, snapshot),
          filters: filtersParams,
          search: undefined,
          invalid: false,
          deadline: false,
          selection: [],
          page: 0,
        }
      },

      setStatus: (status: Status) => (state) => ({
        status,
        category: getDefaultCategory(status, state.snapshot),
        filters: filtersParams,
        search: undefined,
        invalid: false,
        deadline: false,
        selection: [],
        page: 0,
      }),

      setCategory: (category: string) => ({
        category,
        filters: filtersParams,
        search: undefined,
        invalid: false,
        deadline: false,
        selection: [],
        page: 0,
      }),

      setFilters: (filters: FilterSelection) => {
        setImmediate(() => {
          setFiltersParams(filters)
        })
        return {
          filters,
          search: undefined,
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

  if (state.snapshot !== snapshot) {
    actions.setSnapshot(snapshot)
  }

  return [state, actions] as [typeof state, typeof actions]
}

function getDefaultCategory(status: string, snapshot: Snapshot | undefined) {
  if (snapshot === undefined) return "pending"
  if (status === "drafts") return "pending"

  const count = snapshot.lots

  let pending = 0
  let tofix = 0
  let total = 0

  if (status === "in") {
    pending = count.in_pending
    tofix = count.in_tofix
    total = count.in_total
  } else if (status === "out") {
    pending = count.out_pending
    tofix = count.out_tofix
    total = count.out_total
  } else if (status === "stocks") {
    pending = count.stock
    total = count.stock_total
  }

  if (pending > 0) return "pending"
  else if (tofix > 0) return "correction"
  else if (total > 0) return "history"
  else return "pending"
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
      deadline,
      page,
      limit,
      order,
      filters,
    ]
  )
}

export default Lots
