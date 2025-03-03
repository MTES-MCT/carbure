import useEntity from "common/hooks/entity"
import { Main } from "common/components/scaffold"
import Select from "common/components/select"
import { useQuery } from "common/hooks/async"
import useYears from "common/hooks/years"
import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import * as api from "./api"
import ProvisionList from "./pages/provision-certificates"
import { ElecAdminProvisionCertificateStatus } from "./pages/provision-certificates/types"
import TransferList from "./pages/transfer-certificates"
import { ElecAdminSnapshot } from "./types"

const defaultElecAdminSnapshot: ElecAdminSnapshot = {
  provision_certificates: 0,
  provision_certificates_available: 0,
  provision_certificates_history: 0,
  transfer_certificates: 0,
  transfer_certificates_accepted: 0,
  transfer_certificates_pending: 0,
  transfer_certificates_rejected: 0,
  provisioned_energy: 0,
  transferred_energy: 0,
}

export const ElecAdmin = () => {
  const { t } = useTranslation()

  const entity = useEntity()

  const years = useYears("elec-admin", api.getYears)
  const elecAdminSnapshot = useQuery(api.getSnapshot, {
    key: "elec-admin-snapshot",
    params: [entity.id, years.selected],
  })

  const snapshot =
    elecAdminSnapshot.result?.data.data ?? defaultElecAdminSnapshot

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
          path="provision/*"
          element={<ProvisionList snapshot={snapshot} year={years.selected} />}
        />

        <Route
          path="transfer/*"
          element={<TransferList snapshot={snapshot} year={years.selected} />}
        />
        <Route
          path="*"
          element={
            <Navigate
              replace
              to={`provision/${ElecAdminProvisionCertificateStatus.Available.toLocaleLowerCase()}`}
            />
          }
        />
      </Routes>
    </Main>
  )
}

export default ElecAdmin
