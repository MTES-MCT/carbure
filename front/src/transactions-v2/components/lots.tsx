import { useState } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import * as api from "../api"
import { Entity } from "carbure/types"
import { Lot, Snapshot, Status } from "../types"
import { useQuery } from "common-v2/hooks/async"
import useLotQuery from "../hooks/lot-query"
import useStatus from "../hooks/status"
import { Bar, } from "common-v2/components/scaffold"
import Pagination, { usePagination } from "common-v2/components/pagination"
import Filters, { useFilters } from "../components/filters"
import { LotTable } from "../components/lot-table"
import NoResult from "../components/no-result"
import { LotActions } from "../components/lot-actions"
import {
  CorrectionSwitch,
  DeadlineSwitch,
  InvalidSwitch,
} from "../components/switches"

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
  const [correction, showCorrections] = useState(false)
  const [invalid, showInvalid] = useState(false)
  const [deadline, showDeadline] = useState(false)
  const [search, setSearch] = useState<string | undefined>()
  const [selection, setSelection] = useState<number[]>([])

  const query = useLotQuery({
    entity,
    status,
    sub: category,
    year,
    search,
    correction,
    invalid,
    deadline,
    pagination,
    filters: filters.selected,
  })

  const lots = useQuery(api.getLots, {
    key: "transactions",
    params: [query],
  })

  const count = countLots(status, snapshot)
  const lotsData = lots.result?.data.data
  const lotList = lotsData?.lots ?? []
  const returned = lotsData?.returned ?? 0
  const total = lotsData?.total ?? 0
  const expiration = lotsData?.deadlines ?? { total: 0, date: "" }
  const errors = Object.keys(lotsData?.errors ?? {})

  const open = (lot: Lot) => navigate({
    pathname: `${status}/${lot.id}`,
    search: location.search
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
        <LotActions
          count={returned}
          query={query}
          selection={selection}
          category={category}
          pending={count.pending}
          history={count.history}
          search={search}
          onSwitch={setCategory}
          onSearch={setSearch}
        />

        {count.tofix > 0 && (
          <CorrectionSwitch
            count={count?.tofix}
            active={correction}
            onSwitch={showCorrections}
          />
        )}

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
            onAction={open}
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


function countLots(status: Status, snapshot: Snapshot | undefined) {
  switch (status) {
    case "in":
      return {
        pending: snapshot?.lots.in_pending ?? 0,
        history: snapshot?.lots.in_total ?? 0,
        tofix: snapshot?.lots.in_tofix ?? 0,
      }
    case "out":
      return {
        pending: snapshot?.lots.out_pending ?? 0,
        history: snapshot?.lots.out_total ?? 0,
        tofix: snapshot?.lots.out_tofix ?? 0,
      }
    default:
      return {
        pending: 0,
        history: 0,
        tofix: 0,
      }
  }
}

export default Lots