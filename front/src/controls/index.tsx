import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import useEntity from "carbure/hooks/entity"
import { useQuery } from "common-v2/hooks/async"
import * as api from "./api"
import { Main } from "common-v2/components/scaffold"
import Select from "common-v2/components/select"
import { PortalProvider } from "common-v2/components/portal"
import { StatusTabs, useStatus } from "./components/status"
import Lots from "./components/lots"
import { useYears } from "transactions"

export const Controls = () => {
  const { t } = useTranslation()

  const entity = useEntity()
  const status = useStatus()

  const years = useYears("controls", api.getYears)

  const snapshot = useQuery(api.getSnapshot, {
    key: "snapshot",
    params: [entity.id, years.selected],
  })

  if (status === "unknown") {
    return <Navigate to="alerts" />
  }

  const snapshotData = snapshot.result?.data.data

  // common props for subroutes
  const props = { entity, year: years.selected, snapshot: snapshotData }

  return (
    <PortalProvider>
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
          <Route path="*" element={<Lots {...props} />} />
        </Routes>
      </Main>
    </PortalProvider>
  )
}

export default Controls
