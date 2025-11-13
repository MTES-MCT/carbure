import { useTranslation } from "react-i18next"
import { Route, Routes } from "react-router-dom"
import HashRoute from "common/components/hash-route"
import { Main } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import useYears from "common/hooks/years-2"
import TransferCertificates from "./pages/transfer"
import ProvisionCertificates from "./pages/provision"
import ProvisionCertificateDetails from "./pages/provision-details"
import TransferCertificateDetails from "./pages/transfer-details"
import { getYears, getSnapshot } from "./api"
import useEntity from "common/hooks/entity"
import { ImportProvisionCertificates } from "./components/import-provision-certificates"
import { SendTransferCertificates } from "./components/send-transfer-certificates"
import { useQuery } from "common/hooks/async"
import { useProvisionCertificatesBalance } from "./hooks/provision-certificates.hooks"

export const ElecCertificates = () => {
  const { t } = useTranslation()

  const entity = useEntity()
  const years = useYears("elec-v2/certificates", getYears)

  const snapshot = useQuery(getSnapshot, {
    key: "elec-certificates-snapshot",
    params: [entity.id, years.selected],
  })

  const { balance, formattedBalance } = useProvisionCertificatesBalance()

  const canWriteCPO = entity.isCPO && entity.canWrite()
  const canWriteAdmin =
    (entity.isAdmin || entity.hasAdminRight("ELEC")) && entity.canWrite()

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

          {canWriteCPO && (
            <SendTransferCertificates
              balance={balance}
              formattedBalance={formattedBalance}
            />
          )}
          {canWriteAdmin && <ImportProvisionCertificates />}
        </section>
      </header>

      <Routes>
        <Route
          path="provision/:status?"
          element={
            <ProvisionCertificates
              year={years.selected}
              snapshot={snapshot.result?.data}
              formattedBalance={formattedBalance}
            />
          }
        />
        <Route
          path="transfer/:status?"
          element={
            <TransferCertificates
              year={years.selected}
              snapshot={snapshot.result?.data}
              formattedBalance={formattedBalance}
            />
          }
        />
      </Routes>

      <HashRoute
        path="provision-certificate/:id"
        element={<ProvisionCertificateDetails />}
      />

      <HashRoute
        path="transfer-certificate/:id"
        element={<TransferCertificateDetails />}
      />
    </Main>
  )
}

export default ElecCertificates
