import { useState } from "react"
import { Route, Routes, Navigate, useLocation } from "react-router-dom"
import { useTranslation } from "react-i18next"
import useEntity from "carbure/hooks/entity"
import { useQuery } from "common/hooks/async"
import { Main } from "common/components/scaffold"
import Select from "common/components/select"
import AgreementList from "./components/agreement-list"
import QuotasList from "./components/dc-quotas"
import * as api from "./api"
import useTitle from "common/hooks/title"
import Tabs from "common/components/tabs"
import DoubleCountingFilesChecker from "./components/files-checker"

const DoubleCounting = () => {
  const { t } = useTranslation()
  useTitle(t("Double comptage"))

  const entity = useEntity()
  const location = useLocation()

  const currentYear = new Date().getFullYear()
  const [year, setYear] = useState(currentYear)

  const snapshot = useQuery(api.getDoubleCountingSnapshot, {
    key: "dc-snapshot",
    params: [],
    onSuccess: (snapshot) => {
      const years = snapshot.data.data?.years ?? []
      if (!years.includes(year)) setYear(years[0] ?? currentYear)
    },
  })

  const snapshotData = snapshot.result?.data.data

  return (
    <Main>
      {!location.pathname.includes("/files-checker") && (
        <header>
          <section>
            <h1>{t("Double comptage")}</h1>

            <Select
              variant="inline"
              value={year}
              onChange={(v) => setYear(v as number)}
              defaultOptions={[{ label: `${currentYear}`, value: currentYear }]}
              options={snapshotData?.years.map((year) => ({
                label: `${year}`,
                value: year,
              }))}
            />
          </section>

          <section>
            <Tabs
              variant="main"
              tabs={[
                { key: "agreements", path: "agreements", label: t("Dossiers") },
                { key: "quotas", path: "quotas", label: t("Agréements") },
              ]}
            />
          </section>
        </header>
      )}
      <Routes>
        <Route
          path="agreements"
          element={<AgreementList entity={entity} year={year} />}
        />
        <Route path="quotas" element={<QuotasList year={year} />} />
        <Route
          path="files-checker/*"
          element={<DoubleCountingFilesChecker />}
        />
        <Route path="*" element={<Navigate to="agreements" />} />
      </Routes>
    </Main>
  )
}

export default DoubleCounting
