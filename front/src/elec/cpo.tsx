import useEntity from "common/hooks/entity"
import { Main } from "common/components/scaffold"
import Select from "common/components/select"
import { useQuery } from "common/hooks/async"
import useYears from "common/hooks/years"
import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import * as api from "./api-cpo"
import { ElecCPOProvisionCertificateStatus, ElecCPOSnapshot } from "./types-cpo"
import ProvisionCertificateList from "./components/provision-certificates/list"
import CPOTransferCertificateList from "./components/transfer-certificates/list-cpo"

const defaultElecSnapshot: ElecCPOSnapshot = {
  provisioned_energy: 0,
  remaining_energy: 0,
  provision_certificates_available: 0,
  provision_certificates_history: 0,
  transferred_energy: 0,
  transfer_certificates_pending: 0,
  transfer_certificates_accepted: 0,
  transfer_certificates_rejected: 0,
}

export const ElecCPO = () => {
  const { t } = useTranslation()
  const entity = useEntity()

  const years = useYears("elec", api.getYears)
  const snapshotResponse = useQuery(api.getSnapshot, {
    key: "elec-cpo-snapshot",
    params: [entity.id, years.selected],
  })

  const snapshot = snapshotResponse.result?.data.data ?? defaultElecSnapshot

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
        <Route
          path="provisioned/*"
          element={
            <ProvisionCertificateList
              snapshot={snapshot}
              year={years.selected}
            />
          }
        />
        <Route
          path="transferred/*"
          element={
            <CPOTransferCertificateList
              snapshot={snapshot}
              year={years.selected}
            />
          }
        />

        <Route
          path="*"
          element={
            <Navigate
              replace
              to={`provisioned/${ElecCPOProvisionCertificateStatus.Available.toLocaleLowerCase()}`}
            />
          }
        />
      </Routes>
    </Main>
  )
}

export default ElecCPO
