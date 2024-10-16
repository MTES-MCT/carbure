import useEntity from "carbure/hooks/entity"
import { Main } from "common/components/scaffold"
import Select from "common/components/select"
import { useQuery } from "common/hooks/async"
import useYears from "common/hooks/years"
import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import { Loader } from "common/components/icons"
import Tabs from "common/components/tabs"
import { formatNumber } from "common/utils/formatters"
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
  // const snapshot = elecSnapshot //TODO TEST with testing data

  return (
    <Main>
      <header>
        <section>
          <h1>{t("Électricité renouvelable")}</h1>

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
          <ElecTabs loading={snapshotResponse.loading} snapshot={snapshot} />
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

interface ElecTabsProps {
  loading: boolean
  snapshot: ElecCPOSnapshot
}

function ElecTabs({ loading, snapshot }: ElecTabsProps) {
  const { t } = useTranslation()

  return (
    <Tabs
      variant="main"
      tabs={[
        {
          key: "provisioned",
          path: "provisioned",
          label: (
            <>
              <p
                style={{
                  fontWeight: "normal",
                }}
              >
                {loading ? (
                  <Loader size={20} />
                ) : (
                  formatNumber(snapshot?.remaining_energy, 3)
                )}{" "}
                MWh
              </p>
              <strong>{t("Énergie disponible")}</strong>
            </>
          ),
        },
        {
          key: "transferred",
          path: "transferred",
          label: (
            <>
              <p
                style={{
                  fontWeight: "normal",
                }}
              >
                {loading ? (
                  <Loader size={20} />
                ) : (
                  formatNumber(snapshot?.transferred_energy, 3)
                )}{" "}
                MWh
              </p>
              <strong>{t("Énergie cédée")}</strong>
            </>
          ),
        },
      ]}
    />
  )
}
