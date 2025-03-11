import useEntity from "common/hooks/entity"
import { Main } from "common/components/scaffold"
import Select from "common/components/select"
import { useQuery } from "common/hooks/async"
import useYears from "common/hooks/years"
import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import * as api from "./api-operator"
import { ElecOperatorSnapshot, ElecOperatorStatus } from "./types-operator"
import OperatorTransferCertificateList from "./components/transfer-certificates/list-operator"
import { usePrivateNavigation } from "common/layouts/navigation"

const defaultSnapshot: ElecOperatorSnapshot = {
  transfer_cert_pending: 0,
  transfer_cert_accepted: 0,
  acquired_energy: 0,
}

const ElecOperator = () => {
  const { t } = useTranslation()
  usePrivateNavigation(t("Certificats"))

  const entity = useEntity()

  const years = useYears("elec", api.getOperatorYears)
  const snapshotResponse = useQuery(api.getOperatorSnapshot, {
    key: "elec-operator-snapshot",
    params: [entity.id, years.selected],
  })

  const snapshot = snapshotResponse.result?.data.data ?? defaultSnapshot

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
          path="pending/*"
          element={
            <OperatorTransferCertificateList
              snapshot={snapshot}
              year={years.selected}
            />
          }
        />

        <Route
          path="accepted/*"
          element={
            <OperatorTransferCertificateList
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
              to={`${ElecOperatorStatus.Pending.toLocaleLowerCase()}`}
            />
          }
        />
      </Routes>
    </Main>
  )
}

export default ElecOperator
