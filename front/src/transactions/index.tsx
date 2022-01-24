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

  const years = useYears("transactions", api.getYears)

  const snapshot = useQuery(api.getSnapshot, {
    key: "snapshot",
    params: [entity.id, years.selected],
  })

  if (status === "unknown") {
    return <Navigate to="drafts" />
  }

  const snapshotData = snapshot.result?.data.data

  // common props for subroutes
  const props = { entity, year: years.selected, snapshot: snapshotData }

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
                value={years.selected}
                onChange={years.setYear}
                options={years.data}
                sort={(year) => -year.value}
              />

              <DeclarationButton year={years.selected} years={years.data} />
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

export function useYears(root: string, getYears: typeof api.getYears) {
  const location = useLocation()
  const params = useParams<"year">()
  const navigate = useNavigate()

  const entity = useEntity()

  const selected = parseInt(params.year ?? "") || currentYear

  const setYear = useCallback(
    (year: number | undefined) => {
      const rx = new RegExp(`${root}/[0-9]+`)
      const replacement = `${root}/${year}`
      const pathname = location.pathname.replace(rx, replacement)
      navigate(pathname)
    },
    [root, location, navigate]
  )

  const years = useQuery(getYears, {
    key: "years",
    params: [entity.id],

    // select the latest year if the selected one isn't available anymore
    onSuccess: (res) => {
      const years = res.data.data ?? []
      const year = years.length > 0 ? Math.max(...years) : currentYear
      if (!years.includes(selected)) setYear(year)
    },
  })

  const yearData = years.result?.data.data?.length
    ? years.result?.data.data
    : [currentYear]

  return {
    loading: years.loading,
    data: yearData,
    selected,
    setYear,
  }
}

export default Transactions
