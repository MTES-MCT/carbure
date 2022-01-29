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
import { StatusTabs } from "./components/status"
import { DeclarationButton } from "./actions/declaration"
import { ImportArea } from "./actions/import"
import Lots from "./components/lots"
import Stocks from "./components/stocks"

export const Transactions = () => {
  const { t } = useTranslation()

  const entity = useEntity()

  const years = useYears("transactions", api.getYears)

  const snapshot = useQuery(api.getSnapshot, {
    key: "snapshot",
    params: [entity.id, years.selected],
  })

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
                options={years.options}
                sort={(year) => -year.value}
              />

              <DeclarationButton year={years.selected} years={years.options} />
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
              element={
                // if entity does not have stock redirect to default drafts
                entity.has_stocks ? (
                  <Stocks {...props} />
                ) : (
                  <Navigate replace to="../drafts/pending" />
                )
              }
            />
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
      const years = listYears(res.data.data)
      if (!years.includes(selected)) {
        setYear(Math.max(...years))
      }
    },
  })

  return {
    loading: years.loading,
    options: listYears(years.result?.data.data),
    selected,
    setYear,
  }
}

function listYears(years: number[] | undefined) {
  if (years?.length) return years
  else return [currentYear]
}

export default Transactions
