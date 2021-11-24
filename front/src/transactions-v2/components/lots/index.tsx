import { useEffect, useMemo, useState } from "react"
import { Route, Routes, useNavigate, useLocation } from "react-router-dom"
import * as api from "../../api"
import { Entity } from "carbure/types"
import { Lot, Snapshot, FilterSelection, Status, LotQuery } from "../../types"
import { PaginationManager } from "common-v2/components/pagination"
import { useQuery } from "common-v2/hooks/async"
import { useStatus } from "../status"
import { Order } from "common-v2/components/table"
import { Bar } from "common-v2/components/scaffold"
import Pagination, { usePagination } from "common-v2/components/pagination"
import Filters, { useFilters } from "../filters"
import { LotTable } from "./lot-table"
import NoResult from "../no-result"
import { LotActions } from "./lot-actions"
import { DeadlineSwitch, InvalidSwitch } from "../switches"
import { LotSummaryBar } from "./lot-summary"
import SearchBar from "../search-bar"
import LotAdd from "lot-add"
import LotDetails from "lot-details"

export interface LotsProps {
  entity: Entity
  year: number
  snapshot: Snapshot | undefined
}

const EMPTY: number[] = []

export const Lots = ({ entity, year, snapshot }: LotsProps) => {
  const navigate = useNavigate()
  const location = useLocation()

  const status = useStatus()
  const filters = useFilters()
  const pagination = usePagination()

  const [category, setCategory] = useState("pending")
  const [invalid, showInvalid] = useState(false)
  const [deadline, showDeadline] = useState(false)
  const [search, setSearch] = useState<string | undefined>()
  const [selection, setSelection] = useState<number[]>(EMPTY)
  const [order, setOrder] = useState<Order | undefined>()

  // go back to the first page and empty selection when the query changes
  const { limit, setPage } = pagination
  useEffect(() => {
    setPage(0)
    setSelection(EMPTY)
  }, [
    status,
    filters.selected,
    category,
    invalid,
    deadline,
    search,
    limit,
    setPage,
  ])

  // reset invalid/deadline filters when changing status/category
  useEffect(() => {
    showDeadline(false)
    showInvalid(false)
  }, [status, category])

  // reset category when changing status
  useEffect(() => {
    setCategory("pending")
  }, [status])

  const query = useLotQuery({
    entity,
    status,
    category,
    year,
    search,
    invalid,
    deadline,
    pagination,
    order,
    filters: filters.selected,
  })

  const lots = useQuery(api.getLots, {
    key: "lots",
    params: [query],
  })

  const lotsData = lots.result?.data.data
  const lotList = lotsData?.lots ?? []
  const ids = lotsData?.ids ?? EMPTY
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
          selected={filters.selected}
          onSelect={filters.onFilter}
        />
      </Bar>

      <section>
        <SearchBar
          count={snapshot?.lots}
          search={search}
          category={category}
          onSearch={setSearch}
          onSwitch={setCategory}
        />

        <LotActions count={count} query={query} selection={selection} />

        {totalErrors > 0 && (
          <InvalidSwitch
            count={totalErrors}
            active={invalid}
            onSwitch={showInvalid}
          />
        )}

        {totalDeadline > 0 && (
          <DeadlineSwitch
            count={totalDeadline}
            active={deadline}
            onSwitch={showDeadline}
          />
        )}

        {count === 0 && <NoResult loading={lots.loading} filters={filters} />}

        {count > 0 && (
          <>
            <LotSummaryBar
              query={query}
              selection={selection}
              filters={filters}
            />

            <LotTable
              loading={lots.loading}
              order={order}
              lots={lotList}
              errors={lotErrors}
              selected={selection}
              onSelect={setSelection}
              onAction={showLotDetails}
              onOrder={setOrder}
            />

            <Pagination
              page={pagination.page}
              limit={pagination.limit}
              total={total}
              onPage={pagination.setPage}
              onLimit={pagination.setLimit}
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

export interface LotQueryParams {
  entity: Entity
  status: Status
  category: string
  year: number
  search: string | undefined
  invalid: boolean
  deadline: boolean
  pagination: PaginationManager
  order: Order | undefined
  filters: FilterSelection
}

export function useLotQuery({
  entity,
  status,
  category,
  year,
  search,
  invalid,
  deadline,
  pagination,
  order,
  filters,
}: LotQueryParams) {
  const { page = 0, limit } = pagination

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
