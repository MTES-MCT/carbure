import useEntity from "carbure/hooks/entity"
import { Col, Main, Row } from "common/components/scaffold"
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
import { Loader, Upload } from "common/components/icons"
import Tabs from "common/components/tabs"
import { elecAdminSnapshot } from "./__test__/data"
import { formatNumber } from "common/utils/formatters"
import { ElecAdminSnapshot } from "./types"
import ProvisionList from "./components/provisionList"


const defaultElecAdminSnapshot: ElecAdminSnapshot = {
  provision_certificates: 0,
  transfer_certificates: 0,
  provided_energy: 0,
  transfered_energy: 0
}

export const ElecAdmin = () => {
  const { t } = useTranslation()

  const entity = useEntity()

  const years = useYears("elec-admin", api.getYears)

  const snapshotResponse = useQuery(api.getSnapshot, {
    key: "elec-admin-snapshot",
    params: [entity.id, years.selected],
  })

  // const snapshot = snapshotResponse.result?.data.data ?? defaultElecAdminSnapshot
  const snapshot = elecAdminSnapshot ?? defaultElecAdminSnapshot //TO TEST with testing data

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
            <h1>{t("Électricité")}</h1>
          </section>

          <section>
            <ElecAdminTabs loading={snapshotResponse.loading} snapshot={snapshot} />
          </section>
        </header>


        <Routes>
          <Route
            path="provision/*"
            element={
              <ProvisionList snapshot={snapshot} />
            }
          />

        </Routes>
      </Main>
    </FileArea>
  )
}

export default ElecAdmin



interface ElecAdminTabsProps {
  loading: boolean
  snapshot: ElecAdminSnapshot
}


function ElecAdminTabs({
  loading,
  snapshot
}: ElecAdminTabsProps) {
  const { t } = useTranslation()

  return (<Tabs variant="main" tabs={[{
    key: "provision",
    path: "provision",
    label: <>
      <p style={{
        fontWeight: "normal"
      }}>
        {loading ? <Loader size={20} /> : formatNumber(snapshot?.provided_energy)}
      </p>
      <strong>
        {t("Énergie attribuée")}
      </strong>
    </>
  }, {
    key: "transfer",
    path: "transfer",
    label: <>
      <p style={{
        fontWeight: "normal"
      }}>
        {loading ? <Loader size={20} /> : formatNumber(snapshot?.transfered_energy)}
      </p>
      <strong>
        {t("Énergie cédée")}
      </strong>
    </>
  }]} />);
}

