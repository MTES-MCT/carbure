import { useState } from "react"
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

const currentYear = new Date().getFullYear()

export const Controls = () => {
  const { t } = useTranslation()

  const entity = useEntity()
  const status = useStatus()

  const [year = currentYear, setYear] = useState<number | undefined>(currentYear) // prettier-ignore

  const years = useQuery(api.getYears, {
    key: "years",
    params: [entity.id],

    // select the latest year if the selected one isn't available anymore
    onSuccess: (res) => {
      const years = res.data.data ?? []
      if (!years.includes(year)) {
        setYear(Math.max(...years))
      }
    },
  })

  const snapshot = useQuery(api.getSnapshot, {
    key: "snapshot",
    params: [entity.id, year],
  })

  if (status === "unknown") {
    return <Navigate to="alerts" />
  }

  const yearData = years.result?.data.data
  const snapshotData = snapshot.result?.data.data

  // common props for subroutes
  const props = { entity, year, snapshot: snapshotData }

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
              value={year}
              onChange={setYear}
              options={yearData}
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
