import { Main } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import useYears from "common/hooks/years-2"
import { FetchResponseType } from "common/services/api-fetch.types"
import { useTranslation } from "react-i18next"
import { Route, Routes } from "react-router-dom"
import TransferCertificates from "./pages/transfer"
import ProvisionCertificates from "./pages/provision"

async function getYears() {
  return { data: [2025] } as FetchResponseType<number[]>
}

export const ElecCertificates = () => {
  const { t } = useTranslation()

  const years = useYears("elec-v2", getYears)

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
        <Route path="transfer/:status?" element={<TransferCertificates />} />
      </Routes>
    </Main>
  )
}

export default ElecCertificates
