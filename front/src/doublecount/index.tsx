import { useState } from "react"
import { Route, Routes, Navigate } from "react-router-dom"
import { Trans, useTranslation } from "react-i18next"
import useEntity from "carbure/hooks/entity"
import { useQuery } from "common/hooks/async"
import { Main } from "common/components/scaffold"
import Select from "common/components/select"
import AgreementList from "./components/agreement-list"
import QuotasList from "./components/dc-quotas"
import * as api from "./api"
import useTitle from "common/hooks/title"
import Tabs from "common/components/tabs"

const DoubleCounting = () => {
  const { t } = useTranslation()
  useTitle(t("Double comptage"))

  const entity = useEntity()

  const [year, setYear] = useState(new Date().getFullYear())
  const snapshot = useQuery(api.getDoubleCountingSnapshot, {
    key: "dc-snapshot",
    params: [],
    onSuccess: (snapshot) => {
      const years = snapshot.data.data?.years ?? []
      if (!years.includes(year)) setYear(years[0])
    },
  })

  const snapshotData = snapshot.result?.data.data

  return (
    <Main>
      <header>
        <section>
          <h1>{t("Double comptage")}</h1>

          <Select
            variant="inline"
            value={year}
            onChange={(v) => setYear(v as number)}
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
              { key: "quotas", path: "quotas", label: t("Quotas") },
            ]}
          />
        </section>
      </header>

      <Routes>
        <Route
          path="agreements"
          element={<AgreementList entity={entity} year={year} />}
        />
        <Route path="quotas" element={<QuotasList year={year} />} />
        <Route path="*" element={<Navigate to="agreements" />} />
      </Routes>
    </Main>
  )
}

export default DoubleCounting
