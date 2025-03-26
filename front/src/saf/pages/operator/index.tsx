import useEntity from "common/hooks/entity"
import { Main } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import { useQuery } from "common/hooks/async"
import useYears from "common/hooks/years-2"
import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import { getYears, getSnapshot } from "saf/api"
import TicketSources from "./pages/ticket-sources"
import OperatorTickets from "./pages/tickets"
import { SafTicketSourceStatus } from "./types"
import { SafOperatorSnapshot } from "saf/types"

export const SafOperator = () => {
  const { t } = useTranslation()

  const entity = useEntity()

  const years = useYears("saf", getYears)

  const snapshot = useQuery(getSnapshot, {
    key: "operator-snapshot",
    params: [entity.id, years.selected],
  })

  const snapshotData = snapshot.result?.data as SafOperatorSnapshot

  return (
    <Main>
      <header>
        <section>
          <Select
            loading={years.loading}
            placeholder={t("Choisir une année")}
            value={years.selected}
            onChange={years.setYear}
            options={years.options}
            sort={(year) => -year.value}
          />
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
              to={SafTicketSourceStatus.AVAILABLE.toLocaleLowerCase()}
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
              to={`ticket-sources/${SafTicketSourceStatus.AVAILABLE.toLocaleLowerCase()}`}
            />
          }
        />
      </Routes>
    </Main>
  )
}

export default SafOperator
