import { useMemo, useState } from "react"
import { useTranslation } from "react-i18next"
import { useQuery } from "common-v2/hooks/async"
import { Bar, Main } from "common-v2/components/scaffold"
import Select from "common-v2/components/select"
import Button from "common-v2/components/button"
import { PortalProvider, usePortal } from "common-v2/components/portal"
import useEntity from "carbure/hooks/entity"
import Filters, { normalizeFilters, useFilters } from "./components/filters"
import { FilterSelection, Lot, LotQuery } from "./types"
import { Certificate, Check } from "common-v2/components/icons"
import Menu from "common-v2/components/menu"
import Dialog from "common-v2/components/dialog"
import { LotTable } from "./components/lot-table"
import NoResult from "./components/no-result"
import { SendButton } from "./actions/send"
import StatusTabs from "./components/status-tabs"
import useStatus from "./hooks/status"
import * as api from "./api"

export const Transactions = () => {
  const { t } = useTranslation()

  const entity = useEntity()
  const status = useStatus()
  const filters = useFilters()
  const [selection, setSelection] = useState<Lot[]>([])
  const [year = 2021, setYear] = useState<number | undefined>()

  const query = useLotQueryParams(entity.id, status, year, filters.selected)

  const snapshotQuery = useQuery(api.getSnapshot, {
    key: "transactions-snapshot",
    params: [entity.id, year],
  })

  const lotsQuery = useQuery(api.getLots, {
    key: "transactions",
    params: [query],
  })

  const snapshot = snapshotQuery.result?.data.data
  const lots = lotsQuery.result?.data.data?.lots ?? []
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
          <div>
            <SendButton query={query} selection={selectionIDs} />
            <Menu
              variant="success"
              icon={Check}
              label="Accepter tout"
              items={[
                { label: t("Incorporation") },
                { label: t("Mise à consommation") },
                {
                  label: t("Livraison directe"),
                  action: () =>
                    portal((close) => (
                      <Dialog onClose={close}>
                        <header>
                          <h1>Livraison directe</h1>
                        </header>
                        <main>
                          <section>Description</section>
                        </main>
                        <footer>
                          <Button aside label="Annuler" action={close} />
                        </footer>
                      </Dialog>
                    )),
                },
              ]}
            />
          </div>

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
        </section>
      </Main>
    </PortalProvider>
  )
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

export default Transactions
