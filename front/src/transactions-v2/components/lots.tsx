import { useEffect, useState } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import * as api from "../api"
import { Entity } from "carbure/types"
import { Lot, Snapshot } from "../types"
import { useQuery } from "common-v2/hooks/async"
import useLotQuery from "../hooks/lot-query"
import useStatus from "../hooks/status"
import { Bar } from "common-v2/components/scaffold"
import Pagination, { usePagination } from "common-v2/components/pagination"
import Filters, { useFilters } from "../components/filters"
import { LotTable } from "../components/lot-table"
import NoResult from "../components/no-result"
import { LotActions } from "../components/lot-actions"
import { DeadlineSwitch, InvalidSwitch } from "../components/switches"
import { SearchBar } from "./search-bar"

export interface LotsProps {
  entity: Entity
  year: number
  snapshot: Snapshot | undefined
}

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
  const [selection, setSelection] = useState<number[]>([])

  // go back to the first page when the query changes
  const { resetPage } = pagination
  useEffect(() => resetPage(), [status, filters.selected, category, invalid, deadline, search, resetPage]) // prettier-ignore

  const query = useLotQuery({
    entity,
    status,
    category,
    year,
    search,
    invalid,
    deadline,
    pagination,
    filters: filters.selected,
  })

  const lots = useQuery(api.getLots, {
    key: "transactions",
    params: [query],
  })

  const lotsData = lots.result?.data.data
  const lotList = lotsData?.lots ?? []
  const returned = lotsData?.returned ?? 0
  const total = lotsData?.total ?? 0
  const expiration = lotsData?.deadlines ?? { total: 0, date: "" }
  const errors = Object.keys(lotsData?.errors ?? {})

  const showDetails = (lot: Lot) =>
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

        <LotActions count={returned} query={query} selection={selection} />

        {errors.length > 0 && (
          <InvalidSwitch
            count={errors.length}
            active={invalid}
            onSwitch={showInvalid}
          />
        )}

        {expiration.total > 0 && (
          <DeadlineSwitch
            count={expiration.total}
            date={expiration.date}
            active={deadline}
            onSwitch={showDeadline}
          />
        )}

        {returned === 0 && (
          <NoResult
            loading={lots.loading}
            count={filters.count}
            onReset={filters.resetFilters}
          />
        )}

        {returned > 0 && (
          <LotTable
            loading={lots.loading}
            lots={lotList}
            selected={selection}
            onSelect={setSelection}
            onAction={showDetails}
          />
        )}

        <Pagination
          page={pagination.page}
          limit={pagination.limit}
          total={total}
          onPage={pagination.setPage}
          onLimit={pagination.setLimit}
        />
      </section>
    </>
  )
}

export default Lots
