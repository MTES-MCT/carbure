import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import useEntity from "carbure/hooks/entity"
import { useQuery } from "common-v2/hooks/async"
import useStatus from "./hooks/status"
import * as api from "./api"
import { Main } from "common-v2/components/scaffold"
import Select from "common-v2/components/select"
import { PortalProvider } from "common-v2/components/portal"
import StatusTabs from "./components/status-tabs"
import { DeclarationButton } from "./actions/declaration"
import Lots from "./components/lots"
import Stocks from "./components/stocks"
import LotAdd from "lot-add"
import LotDetails from "lot-details"
import StockDetails from "stock-details"

export const Transactions = () => {
  const { t } = useTranslation()

  const entity = useEntity()
  const status = useStatus()

  const [year = 2021, setYear] = useState<number | undefined>()

  const snapshot = useQuery(api.getSnapshot, {
    key: "transactions-snapshot",
    params: [entity.id, year],
  })

  if (status === "unknown") {
    return <Navigate to="drafts" />
  }

  const snapshotData = snapshot.result?.data.data

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

        <Routes>
          <Route
            path="stocks/*"
            element={<Stocks entity={entity} snapshot={snapshotData} />}
          />
          <Route
            path="*"
            element={<Lots entity={entity} year={year} snapshot={snapshotData} />} // prettier-ignore
          />
        </Routes>
      </Main>

      <Routes>
        <Route path="drafts/add" element={<LotAdd />} />
        <Route path="stocks/:id" element={<StockDetails />} />
        <Route path=":status/:id" element={<LotDetails />} />
      </Routes>
    </PortalProvider>
  )
}

export default Transactions
