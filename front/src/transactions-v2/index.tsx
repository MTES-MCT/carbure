import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import useEntity from "carbure/hooks/entity"
import { useQuery } from "common-v2/hooks/async"
import useStatus from "./hooks/status"
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
import * as api from "./api"
import { Lot } from "./types"
import { DeadlineSwitch, InvalidSwitch } from "./components/switches"
import TransactionAdd from "transaction-add"

export const Transactions = () => {
  const { t } = useTranslation()

  const entity = useEntity()
  const status = useStatus()
  const filters = useFilters()
  const pagination = usePagination()

  const [hasDeadline, showDeadline] = useState(false)
  const [hasErrors, showErrors] = useState(false)
  const [search, setSearch] = useState<string | undefined>()
  const [selection, setSelection] = useState<Lot[]>([])
  const [year = 2021, setYear] = useState<number | undefined>()

  const query = useLotQuery(
    entity.id,
    status,
    year,
    search,
    hasErrors,
    hasDeadline,
    pagination,
    filters.selected
  )

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

  const lotsData = lots.result?.data.data
  const snapshotData = snapshot.result?.data.data

  const lotList = lotsData?.lots ?? []
  const count = lotsData?.returned ?? 0
  const total = lotsData?.total ?? 0
  const deadline = lotsData?.deadlines ?? { total: 0, date: "" }
  const errors = Object.keys(lotsData?.errors ?? {})

  const selectionIDs = selection.map((lot) => lot.id)

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
            count={count}
            query={query}
            selection={selectionIDs}
            search={search}
            onSearch={setSearch}
          />

          {errors.length > 0 && (
            <InvalidSwitch
              total={errors.length}
              active={hasErrors}
              onSwitch={showErrors}
            />
          )}

          {deadline.total > 0 && (
            <DeadlineSwitch
              total={deadline.total}
              date={deadline.date}
              active={hasDeadline}
              onSwitch={showDeadline}
            />
          )}

          {count === 0 && (
            <NoResult
              loading={lots.loading}
              onReset={filters.resetFilters}
              filterCount={filters.count}
            />
          )}

          {count > 0 && (
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

export default Transactions
