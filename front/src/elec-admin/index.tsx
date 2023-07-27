import useEntity from "carbure/hooks/entity"
import { Main } from "common/components/scaffold"
import Select from "common/components/select"
import { useMutation, useQuery } from "common/hooks/async"
import useYears from "common/hooks/years"
import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
// import OperatorTabs from "./components/operator-tabs"
// import TicketSources from "./components/ticket-sources"
// import OperatorTickets from "./components/tickets/operator-tickets"
import * as api from "./api"
import Button from "common/components/button"
import { FileArea } from "common/components/input"
import { Upload } from "common/components/icons"

export const ElecAdmin = () => {
  const { t } = useTranslation()

  const entity = useEntity()

  const years = useYears("elec-admin", api.getYears)

  const snapshot = useQuery(api.getSnapshot, {
    key: "elec-admin-snapshot",
    params: [entity.id, years.selected],
  })

  const snapshotData = snapshot.result?.data.data
  // const snapshotData = safOperatorSnapshot //TO TEST with testing data

  const importCertificates = useMutation(api.importCertificates)

  return (
    <FileArea
      icon={Upload}
      label={t("Importer le fichier\nsur la plateforme")}
      onChange={(file) => file && importCertificates.execute(entity.id, file)}
    >
      <Main>
        <header>
          <section>
            <h1>{t("Certificats de fournitures et de cession")}</h1>

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
            {/* <OperatorTabs loading={snapshot.loading} count={snapshotData} /> */}
          </section>
        </header>
      </Main>
    </FileArea>
  )
  /* <Routes>
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
          element={
            <OperatorTickets year={years.selected} snapshot={snapshotData} />
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
      </Routes> */
}

export default ElecAdmin
