import useEntity from "carbure/hooks/entity"
import { Main } from "common/components/scaffold"
import Select from "common/components/select"
import { useQuery } from "common/hooks/async"
import useYears from "../../hooks/years"
import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import * as api from "./api"
import AirlineTabs from "./tabs"
import AirlineTickets from "./tickets"
import { SafTicketStatus } from "../../types"
import { SafAirlineSnapshot } from "./types"

export const SafAirline = () => {
  const { t } = useTranslation()

  const entity = useEntity()

  const years = useYears("saf", api.getAirlineYears)

  const snapshot = useQuery(api.getAirlineSnapshot, {
    key: "airline-snapshot",
    params: [entity.id, years.selected],
  })
  const snapshotData = snapshot.result?.data as SafAirlineSnapshot

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
          <AirlineTabs loading={snapshot.loading} count={snapshotData} />
        </section>
      </header>

      <Routes>
        {/* //TODO comment merger les deux instructions si dessous  https://stackoverflow.com/questions/47369023/react-router-v4-allow-only-certain-parameters-in-url */}
        <Route
          path="/tickets/pending"
          element={
            <AirlineTickets year={years.selected} snapshot={snapshotData} />
          }
        />
        <Route
          path="/tickets/accepted"
          element={
            <AirlineTickets year={years.selected} snapshot={snapshotData} />
          }
        />

        <Route
          path="*"
          element={
            <Navigate
              replace
              to={`tickets/${SafTicketStatus.PENDING.toLocaleLowerCase()}/`}
            />
          }
        />
      </Routes>
    </Main>
  )
}

export default SafAirline
