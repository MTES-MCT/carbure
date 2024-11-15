import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import useEntity from "carbure/hooks/entity"
import { useQuery } from "common/hooks/async"
import { Main } from "common/components/scaffold"
import Select from "common/components/select"
import StatusTabs, { useStatus } from "./components/status"
import Lots from "./components/lots"

import pickApi from "./api"
import Stocks from "./components/stocks"
import useYears from "common/hooks/years"

export const Controls = () => {
  const { t } = useTranslation()

  const entity = useEntity()
  const status = useStatus()

  const api = pickApi(entity)

  const years = useYears("controls", api.getYears)

  const snapshot = useQuery(api.getSnapshot, {
    key: "controls-snapshot",
    params: [entity.id, years.selected],
  })

  if (status === "unknown") {
    return <Navigate replace to="alerts" />
  }

  const snapshotData = snapshot.result?.data

  // common props for subroutes
  const props = { entity, year: years.selected, snapshot: snapshotData }

  return (
    <Main>
      <header>
        <section>
          <h1>{t("Transactions")}</h1>

          <Select
            loading={years.loading}
            variant="inline"
            placeholder={t("Choisir une année")}
            value={years.selected}
            onChange={years.setYear}
            options={years.options}
            sort={(year) => -year.value}
          />
        </section>

        <section>
          <StatusTabs loading={snapshot.loading} count={snapshotData?.lots} />
        </section>
      </header>

      <Routes>
        <Route path="stocks/*" element={<Stocks {...props} />} />
        <Route path="*" element={<Lots {...props} />} />
      </Routes>
    </Main>
  )
}

export default Controls
