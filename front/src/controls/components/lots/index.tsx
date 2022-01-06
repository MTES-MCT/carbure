import { useMemo } from "react"
import { Route, Routes, useNavigate, useLocation } from "react-router-dom"
import * as api from "../../api"
import { Entity } from "carbure/types"
import { Lot, Snapshot, FilterSelection, Status, LotQuery } from "../../types"
import { useQuery } from "common-v2/hooks/async"
import { useStatus } from "../status"
import { Order } from "common-v2/components/table"
import { Bar } from "common-v2/components/scaffold"
import Pagination, { useLimit } from "common-v2/components/pagination"
import NoResult from "transactions-v2/components/no-result"
import Filters, { useFilterParams } from "../filters"
import { LotTable } from "./lot-table"
import { LotActions } from "./lot-actions"
import { DeadlineSwitch, InvalidSwitch } from "../switches"
import { LotSummaryBar } from "./lot-summary"
import LotAdd from "lot-add"
import LotDetails from "lot-details"
import useStore from "common-v2/hooks/store"

export interface LotsProps {
  entity: Entity
  year: number
  snapshot: Snapshot | undefined
}

export const Lots = ({ entity, year, snapshot }: LotsProps) => {
  const navigate = useNavigate()
  const location = useLocation()

  const status = useStatus()

  const [state, actions] = useLotQueryStore(entity, year, status)
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

  const showLotDetails = (lot: Lot) =>
    navigate({
      pathname: `${status}/${lot.id}`,
      search: location.search,
    })

  return (
    <>
      <Bar>
        <Filters
          status={status}
          query={query}
          filters={state.filters}
          onFilter={actions.setFilters}
        />
      </Bar>

      <section>
        <LotActions
          count={count}
          query={query}
          selection={state.selection}
          search={state.search}
          onSearch={actions.setSearch}
          onSwitch={actions.setCategory}
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

export interface LotQueryState {
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
}

function useLotQueryStore(entity: Entity, year: number, status: Status) {
  const [limit, saveLimit] = useLimit()
  const [filtersParams, setFiltersParams] = useFilterParams()

  const [state, actions] = useStore(
    {
      entity,
      year,
      status,
      category: "pending",
      filters: filtersParams,
      search: undefined,
      invalid: false,
      deadline: false,
      order: undefined,
      selection: [],
      page: 0,
      limit,
    } as LotQueryState,
    {
      setEntity: (entity: Entity) => ({
        entity,
        category: "pending",
        filters: {},
        search: "",
        invalid: false,
        deadline: false,
        selection: [],
        page: 0,
      }),

      setYear: (year: number) => ({
        year,
        category: "pending",
        filters: {},
        search: "",
        invalid: false,
        deadline: false,
        selection: [],
        page: 0,
      }),

      setStatus: (status: Status) => ({
        status,
        category: "pending",
        filters: {},
        search: "",
        invalid: false,
        deadline: false,
        selection: [],
        page: 0,
      }),

      setCategory: (category: string) => ({
        category,
        filters: {},
        search: "",
        invalid: false,
        deadline: false,
        selection: [],
        page: 0,
      }),

      setFilters: (filters: FilterSelection) => {
        setFiltersParams(filters)
        return {
          filters,
          search: "",
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
    actions.setStatus(status)
  }

  return [state, actions] as [typeof state, typeof actions]
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
}: LotQueryState) {
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
