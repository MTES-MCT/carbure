import { useTranslation } from "react-i18next"
import { Route, Routes } from "react-router-dom"
import HashRoute from "common/components/hash-route"
import { Main } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import useYears from "common/hooks/years-2"
import TransferCertificates from "./pages/transfer"
import ProvisionCertificates from "./pages/provision"
import ProvisionCertificateDetails from "./pages/provision-details"
import { getYears } from "./api"

export const ElecCertificates = () => {
  const { t } = useTranslation()

  const years = useYears("elec-v2/certificates", getYears)

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
        <Route
          path="provision/:status?"
          element={<ProvisionCertificates year={years.selected} />}
        />
        <Route
          path="transfer/:status?"
          element={<TransferCertificates year={years.selected} />}
        />
      </Routes>

      <HashRoute
        path="provision-certificate/:id"
        element={<ProvisionCertificateDetails />}
      />
    </Main>
  )
}

export default ElecCertificates
