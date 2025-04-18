import { Content, Main } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import useYears from "common/hooks/years-2"
import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import { getYears } from "saf/api"
import AirlineTickets from "./pages/tickets"
import { SafTicketStatus } from "../../types"

export const SafAirline = () => {
  const { t } = useTranslation()

  const years = useYears("saf", getYears)

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

      <Content marginTop>
        <Routes>
          {/* //TODO comment merger les deux instructions si dessous  https://stackoverflow.com/questions/47369023/react-router-v4-allow-only-certain-parameters-in-url */}
          <Route
            path="/tickets/pending"
            element={<AirlineTickets year={years.selected} />}
          />
          <Route
            path="/tickets/accepted"
            element={<AirlineTickets year={years.selected} />}
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
      </Content>
    </Main>
  )
}

export default SafAirline
