import useEntity from "carbure/hooks/entity"
import { Main } from "common/components/scaffold"
import Select from "common/components/select"
import { useQuery } from "common/hooks/async"
import useYears from "common/hooks/years"
import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import * as api from "./api"
import OperatorTabs from "./components/operator-tabs"
import TicketSources from "./components/ticket-sources"
import OperatorTickets from "./components/tickets/operator-tickets"
import { SafTicketSourceStatus } from "./types"

export const Saf = () => {
  const { t } = useTranslation()

  const entity = useEntity()

  const years = useYears("saf", api.getOperatorYears)

  const snapshot = useQuery(api.getOperatorSnapshot, {
    key: "operator-snapshot",
    params: [entity.id, years.selected],
  })

  const snapshotData = snapshot.result?.data.data

  return (
    <Main>
      <header>
        <section>
          <h1>{t("Carburant Durable d'Aviation")}</h1>

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
          path="tickets-received/*"
          element={
            <OperatorTickets
              type="received"
              year={years.selected}
              snapshot={snapshotData}
            />
          }
        />

        <Route
          path="tickets-assigned/*"
          element={
            <OperatorTickets
              type="assigned"
              year={years.selected}
              snapshot={snapshotData}
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
  )
}

export default Saf
