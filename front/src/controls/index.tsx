import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import useEntity from "common/hooks/entity"
import { useQuery } from "common/hooks/async"
import { Main } from "common/components/scaffold"
import Select from "common/components/select"
import { useStatus } from "./components/status"
import { useRouteBase } from "common/hooks/route-base"
import Lots from "./components/lots"

import pickApi from "./api"
import Stocks from "./components/stocks"
import useYears from "common/hooks/years"

export const Controls = () => {
  const basePath = useRouteBase("/org/:entity/controls/:year/*")
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
    return <Navigate replace to={`${basePath}/alerts`} />
  }

  const snapshotData = snapshot.result?.data.data

  // common props for subroutes
  const props = { entity, year: years.selected, snapshot: snapshotData }

  return (
    <Main>
      <header>
        <section>
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
      </header>

      <Routes>
        <Route path="stocks/*" element={<Stocks {...props} />} />
        <Route path="*" element={<Lots {...props} />} />
      </Routes>
    </Main>
  )
}

export default Controls
