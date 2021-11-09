import { useMemo, useState } from "react"
import { useTranslation } from "react-i18next"
import { useMatch } from "react-router-dom"
import { useQuery } from "common-v2/hooks/async"
import { Bar, Main, LoaderOverlay } from "common-v2/components/scaffold"
import Select from "common-v2/components/select"
import Button from "common-v2/components/button"
import useEntity from "carbure/hooks/entity"
import * as api from "./api"
import StatusTabs from "./components/status-tabs"
import Filters, {
  DRAFT_FILTERS,
  normalizeFilters,
  useFilters,
} from "./components/filters"
import { FilterSelection, Lot, LotQuery } from "./types"
import { Certificate } from "common-v2/components/icons"
import { LotTable } from "./components/lot-table"
import NoResult from "./components/no-result"

const URL_TO_STATUS = {
  draft: "DRAFT",
  in: "IN",
  stock: "STOCK",
  out: "OUT",
  unknown: "UNKNOWN",
}

function useStatus() {
  const match = useMatch<"status">("/org/:entity/transactions-v2/:status")
  const urlStatus = match?.params.status as keyof typeof URL_TO_STATUS ?? "unknown" // prettier-ignore
  return URL_TO_STATUS[urlStatus]
}

function useLotQueryParams(
  entityID: number,
  status: string,
  year: number,
  filters: FilterSelection
) {
  return useMemo<LotQuery>(
    () => ({
      entity_id: entityID,
      year,
      status,
      ...normalizeFilters(filters),
    }),
    [entityID, year, status, filters]
  )
}

export const Transactions = () => {
  const entity = useEntity()
  const { t } = useTranslation()

  const status = useStatus()

  const [selected, setSelected] = useState<Lot[]>([])
  const [year = 2021, setYear] = useState<number | undefined>()

  const filters = useFilters()

  const queryParams = useLotQueryParams(
    entity.id,
    status,
    year,
    filters.selected
  )

  const snapshotQuery = useQuery(api.getSnapshot, {
    key: "transactions-snapshot",
    params: [entity.id, year],
  })

  const lotsQuery = useQuery(api.getLots, {
    key: "transactions",
    params: [queryParams],
  })

  const lots = lotsQuery.result?.data.data?.lots ?? []

  return (
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
            count={snapshotQuery.result?.data.data?.lots}
          />
        </section>
      </header>

      <Bar>
        <Filters
          fields={DRAFT_FILTERS}
          query={queryParams}
          selected={filters.selected}
          onSelect={filters.onFilter}
        />
      </Bar>

      <section>
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
            selected={selected}
            onSelect={setSelected}
          />
        )}
      </section>
    </Main>
  )
}

export default Transactions
