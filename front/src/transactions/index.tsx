import { useCallback } from "react"
import { useTranslation } from "react-i18next"
import {
  Navigate,
  Route,
  Routes,
  useNavigate,
  useParams,
  useLocation,
} from "react-router-dom"
import useEntity from "carbure/hooks/entity"
import { useQuery } from "common-v2/hooks/async"
import * as api from "./api"
import { Main } from "common-v2/components/scaffold"
import Select from "common-v2/components/select"
import { PortalProvider } from "common-v2/components/portal"
import { StatusTabs, useStatus } from "./components/status"
import { DeclarationButton } from "./actions/declaration"
import { ImportArea } from "./actions/import"
import Lots from "./components/lots"
import Stocks from "./components/stocks"

export const Transactions = () => {
  const { t } = useTranslation()

  const entity = useEntity()
  const status = useStatus()

  const [year, setYear] = useYear("transactions")

  const years = useQuery(api.getYears, {
    key: "years",
    params: [entity.id],

    // select the latest year if the selected one isn't available anymore
    onSuccess: (res) => {
      const years = res.data.data ?? []
      if (!years.includes(year)) {
        setYear(Math.max(...years))
      }
    },
  })

  const snapshot = useQuery(api.getSnapshot, {
    key: "snapshot",
    params: [entity.id, year],
  })

  if (status === "unknown") {
    return <Navigate to="drafts" />
  }

  const yearData = years.result?.data.data
  const snapshotData = snapshot.result?.data.data

  // common props for subroutes
  const props = { entity, year, snapshot: snapshotData }

  return (
    <PortalProvider>
      <ImportArea>
        <Main>
          <header>
            <section>
              <h1>{t("Transactions")}</h1>

              <Select
                loading={years.loading}
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
            <Route path="stocks/*" element={<Stocks {...props} />} />
            <Route path="*" element={<Lots {...props} />} />
          </Routes>
        </Main>
      </ImportArea>
    </PortalProvider>
  )
}

const currentYear = new Date().getFullYear()

export function useYear(root: string) {
  const location = useLocation()
  const params = useParams<"year">()
  const navigate = useNavigate()

  const year = parseInt(params.year ?? "") || currentYear

  const setYear = useCallback(
    (year: number | undefined) => {
      const rx = new RegExp(`${root}/[0-9]+`)
      const replacement = `${root}/${year}`
      const pathname = location.pathname.replace(rx, replacement)
      navigate(pathname)
    },
    [root, location, navigate]
  )

  return [year, setYear] as [typeof year, typeof setYear]
}

export default Transactions
