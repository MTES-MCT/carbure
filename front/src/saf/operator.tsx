import useEntity from "carbure/hooks/entity"
import { Main } from "common/components/scaffold"
import Select from "common/components/select"
import { useQuery } from "common/hooks/async"
import useYears from "common/hooks/years"
import { useCallback } from "react"
import { useTranslation } from "react-i18next"
import {
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
  useParams,
} from "react-router-dom"
import { ImportArea } from "../transactions/actions/import"
import * as api from "./api"
import OperatorTabs from "./components/operator-tabs"
import TicketSources from "./components/ticket-sources"
import Tickets from "./components/tickets"
import { SafTicketSourceStatus, SafTicketStatus } from "./types"
import { safOperatorSnapshot } from "./__test__/data"

export const Saf = () => {
  const { t } = useTranslation()

  const entity = useEntity()

  const years = useYears("saf", api.getOperatorYears)

  const snapshot = useQuery(api.getOperatorSnapshot, {
    key: "operator-snapshot",
    params: [entity.id, years.selected],
  })
  const snapshotData = snapshot.result?.data.data
  // const snapshotData = safOperatorSnapshot //TO TEST with testing data

  return (
    <ImportArea>
      <Main>
        <header>
          <section>
            <h1>{t("Carburant Durable d’Aviation - CDA")}</h1>

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
            <OperatorTabs loading={snapshot.loading} count={snapshotData} />
          </section>
        </header>

        <Routes>
          <Route
            path="ticket-sources/*"
            element={
              <TicketSources year={years.selected} snapshot={snapshotData} />
            }
          />
          <Route
            path="ticket-sources"
            element={
              <Navigate
                replace
                to={SafTicketSourceStatus.Available.toLocaleLowerCase()}
              />
            }
          />
          <Route
            path="tickets/*"
            element={<Tickets year={years.selected} snapshot={snapshotData} />}
          />
          <Route
            path="tickets"
            element={
              <Navigate
                replace
                to={SafTicketStatus.Pending.toLocaleLowerCase()}
              />
            }
          />
          <Route
            path="*"
            element={
              <Navigate
                replace
                to={`ticket-sources/${SafTicketSourceStatus.Available.toLocaleLowerCase()}`}
              />
            }
          />
        </Routes>
      </Main>
    </ImportArea>
  )
}

export default Saf
