import { useEffect, useState } from "react"
import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import useEntity from "carbure/hooks/entity"
import { useQuery } from "common-v2/hooks/async"
import * as api from "./api"
import { Main } from "common-v2/components/scaffold"
import Select from "common-v2/components/select"
import { FileArea } from "common-v2/components/input"
import { Upload } from "common-v2/components/icons"
import { PortalProvider } from "common-v2/components/portal"
import { StatusTabs, useStatus } from "./components/status"
import { DeclarationButton } from "./actions/declaration"
import Lots from "./components/lots"
import Stocks from "./components/stocks"

const currentYear = new Date().getFullYear()

export const Transactions = () => {
  const { t } = useTranslation()

  const entity = useEntity()
  const status = useStatus()

  const [year = currentYear, setYear] = useState<number | undefined>(currentYear) // prettier-ignore

  const years = useQuery(api.getYears, {
    key: "years",
    params: [entity.id],
  })

  const snapshot = useQuery(api.getSnapshot, {
    key: "snapshot",
    params: [entity.id, year],
  })

  const yearData = years.result?.data.data
  const snapshotData = snapshot.result?.data.data

  // select first available year if previous selection did not match
  useEffect(() => {
    if (yearData && !yearData.includes(year)) {
      setYear(yearData[0])
    }
  }, [year, yearData])

  if (status === "unknown") {
    return <Navigate to="drafts" />
  }

  return (
    <PortalProvider>
      <FileArea
        icon={Upload}
        label={t("Importer le fichier\nsur la plateforme")}
        onChange={(file) => {}}
      >
        <Main>
          <header>
            <section>
              <h1>{t("Transactions")}</h1>

              <Select
                variant="inline"
                placeholder={t("Choisir une année")}
                value={year}
                onChange={setYear}
                options={yearData}
                sort={(year) => -year.value}
              />

              <DeclarationButton year={year} />
            </section>

            <section>
              <StatusTabs
                loading={snapshot.loading}
                count={snapshotData?.lots}
              />
            </section>
          </header>

          <Routes>
            <Route
              path="stocks/*"
              element={<Stocks entity={entity} snapshot={snapshotData} />}
            />
            <Route
              path="*"
              element={<Lots entity={entity} year={year} snapshot={snapshotData} />} // prettier-ignore
            />
          </Routes>
        </Main>
      </FileArea>
    </PortalProvider>
  )
}

export default Transactions
