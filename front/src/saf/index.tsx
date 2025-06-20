import useEntity from "common/hooks/entity"
import { Main } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import { useQuery } from "common/hooks/async"
import useYears from "common/hooks/years-2"
import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import { getYears, getSnapshot } from "saf/api"
import { SafTicketSources } from "./pages/ticket-sources"
import { SafTickets } from "./pages/tickets"
import LotDetails from "transaction-details/components/lots"
import HashRoute from "common/components/hash-route"

export const Saf = () => {
  const { t } = useTranslation()

  const entity = useEntity()
  const years = useYears("saf", getYears)

  const snapshot = useQuery(getSnapshot, {
    key: "saf-snapshot",
    params: [entity.id, years.selected],
  })

  const snapshotData = snapshot.result?.data

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
        {!entity.isAirline && (
          <Route
            path="ticket-sources/:status?"
            element={
              <SafTicketSources year={years.selected} snapshot={snapshotData} />
            }
          />
        )}

        <Route
          path="tickets-received/:status?"
          element={
            <SafTickets
              type="received"
              year={years.selected}
              snapshot={snapshotData}
            />
          }
        />

        {!entity.isAirline && (
          <Route
            path="tickets-assigned/:status?"
            element={
              <SafTickets
                type="assigned"
                year={years.selected}
                snapshot={snapshotData}
              />
            }
          />
        )}

        <Route
          path="*"
          element={
            <Navigate
              replace
              to={
                entity.isAirline
                  ? "tickets-received/pending"
                  : "ticket-sources/available"
              }
            />
          }
        />
      </Routes>

      <HashRoute path="lot/:id" element={<LotDetails />} />
    </Main>
  )
}

export default Saf
