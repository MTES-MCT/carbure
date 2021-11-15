import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import useEntity from "carbure/hooks/entity"
import { useQuery } from "common-v2/hooks/async"
import useStatus, { Status } from "./hooks/status"
import useLotQuery from "./hooks/query"
import { Bar, Main } from "common-v2/components/scaffold"
import Select from "common-v2/components/select"
import { PortalProvider } from "common-v2/components/portal"
import Pagination, { usePagination } from "common-v2/components/pagination"
import Filters, { useFilters } from "./components/filters"
import { LotTable } from "./components/lot-table"
import NoResult from "./components/no-result"
import StatusTabs from "./components/status-tabs"
import { Actions } from "./components/actions"
import { DeclarationButton } from "./actions/declaration"
import {
  CorrectionSwitch,
  DeadlineSwitch,
  InvalidSwitch,
} from "./components/switches"
import TransactionAdd from "transaction-add"
import * as api from "./api"
import { Snapshot } from "./types"

export const Transactions = () => {
  const { t } = useTranslation()

  const entity = useEntity()
  const status = useStatus()
  const filters = useFilters()
  const pagination = usePagination()

  const [sub, setSub] = useState("pending")
  const [correction, showCorrections] = useState(false)
  const [invalid, showInvalid] = useState(false)
  const [deadline, showDeadline] = useState(false)
  const [search, setSearch] = useState<string | undefined>()
  const [selection, setSelection] = useState<number[]>([])
  const [year = 2021, setYear] = useState<number | undefined>()

  const query = useLotQuery({
    entity,
    status,
    sub,
    year,
    search,
    correction,
    invalid,
    deadline,
    pagination,
    filters: filters.selected,
  })

  const snapshot = useQuery(api.getSnapshot, {
    key: "transactions-snapshot",
    params: [entity.id, year],
  })

  const lots = useQuery(api.getLots, {
    key: "transactions",
    params: [query],
  })

  if (status === "UNKNOWN") {
    return <Navigate to="draft" />
  }

  const snapshotData = snapshot.result?.data.data
  const count = getCount(status, snapshotData)

  const lotsData = lots.result?.data.data
  const lotList = lotsData?.lots ?? []
  const returned = lotsData?.returned ?? 0
  const total = lotsData?.total ?? 0
  const expiration = lotsData?.deadlines ?? { total: 0, date: "" }
  const errors = Object.keys(lotsData?.errors ?? {})

  return (
    <PortalProvider>
      <Main>
        <header>
          <section>
            <h1>{t("Transactions")}</h1>

            <Select
              variant="inline"
              placeholder={t("Choisir une année")}
              value={year}
              onChange={setYear}
              options={[2019, 2020, 2021]}
            />

            <DeclarationButton />
          </section>

          <section>
            <StatusTabs loading={snapshot.loading} count={snapshotData?.lots} />
          </section>
        </header>

        <Bar>
          <Filters
            status={status}
            query={query}
            selected={filters.selected}
            onSelect={filters.onFilter}
          />
        </Bar>

        <section>
          <Actions
            count={returned}
            query={query}
            selection={selection}
            sub={sub}
            pending={count.pending}
            history={count.history}
            search={search}
            onSwitch={setSub}
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
      </Main>

      <Routes>
        <Route path="draft/add" element={<TransactionAdd />} />
      </Routes>
    </PortalProvider>
  )
}

function getCount(status: Status, snapshot: Snapshot | undefined) {
  switch (status) {
    case "IN":
      return {
        pending: snapshot?.lots.in_pending ?? 0,
        history: snapshot?.lots.in_accepted ?? 0,
        tofix: snapshot?.lots.in_tofix ?? 0,
      }
    case "OUT":
      return {
        pending: snapshot?.lots.out_pending ?? 0,
        history: snapshot?.lots.out_accepted ?? 0,
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

export default Transactions
