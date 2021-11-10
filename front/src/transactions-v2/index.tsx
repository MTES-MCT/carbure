import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Navigate } from "react-router"
import useEntity from "carbure/hooks/entity"
import { useQuery } from "common-v2/hooks/async"
import useStatus from "./hooks/status"
import useLotQuery from "./hooks/query"
import { Bar, Main } from "common-v2/components/scaffold"
import Select from "common-v2/components/select"
import Button from "common-v2/components/button"
import { PortalProvider } from "common-v2/components/portal"
import Pagination, { usePagination } from "common-v2/components/pagination"
import Filters, { useFilters } from "./components/filters"
import { Certificate } from "common-v2/components/icons"
import { LotTable } from "./components/lot-table"
import NoResult from "./components/no-result"
import StatusTabs from "./components/status-tabs"
import { Actions } from "./components/actions"
import * as api from "./api"
import { Lot } from "./types"

export const Transactions = () => {
  const { t } = useTranslation()

  const entity = useEntity()
  const status = useStatus()
  const filters = useFilters()
  const pagination = usePagination()

  const [selection, setSelection] = useState<Lot[]>([])
  const [year = 2021, setYear] = useState<number | undefined>()

  const query = useLotQuery(
    entity.id,
    status,
    year,
    filters.selected,
    pagination
  )

  const snapshotQuery = useQuery(api.getSnapshot, {
    key: "transactions-snapshot",
    params: [entity.id, year],
  })

  const lotsQuery = useQuery(api.getLots, {
    key: "transactions",
    params: [query],
  })

  if (status === "UNKNOWN") {
    return <Navigate to="draft" />
  }

  const snapshot = snapshotQuery.result?.data.data
  const lots = lotsQuery.result?.data.data?.lots ?? []
  const total = lotsQuery.result?.data.data?.total ?? 0
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

            <Button
              aside
              variant="primary"
              icon={Certificate}
              label={t("Valider ma déclaration")}
            />
          </section>

          <section>
            <StatusTabs
              loading={snapshotQuery.loading}
              count={snapshot?.lots}
            />
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
          <Actions count={lots.length} query={query} selection={selectionIDs} />

          {lots.length === 0 && (
            <NoResult
              loading={lotsQuery.loading}
              onReset={filters.resetFilters}
              filterCount={filters.count}
            />
          )}

          {lots.length > 0 && (
            <LotTable
              loading={lotsQuery.loading}
              lots={lots}
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
    </PortalProvider>
  )
}

export default Transactions
