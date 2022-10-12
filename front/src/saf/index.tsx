import useEntity from "carbure/hooks/entity"
import { Main } from "common/components/scaffold"
import Select from "common/components/select"
import { useQuery } from "common/hooks/async"
import { useCallback } from "react"
import { useTranslation } from "react-i18next"
import {
  Route,
  Routes,
  useLocation,
  useNavigate,
  useParams,
} from "react-router-dom"
import { ImportArea } from "../transactions/actions/import"
import * as api from "./api"
import OperatorTabs from "./components/operator-tabs"
import TicketSources from "./components/ticket-sources"
import { safOperatorSnapshot } from "./__test__/data"
// import { Tickets  } from "./components/tickets"

export const Saf = () => {
  const { t } = useTranslation()

  const entity = useEntity()

  const years = useYears("saf", api.getYears)

  const snapshot = useQuery(api.getSafOperatorSnapshot, {
    key: "snapshot",
    params: [entity.id, years.selected],
  })

  // const snapshotData = snapshot.result?.data.data
  const snapshotData = safOperatorSnapshot

  return (
    <ImportArea>
      <Main>
        <header>
          <section>
            <h1>{t("Carburant Durable d’Aviation - CDA")}</h1>

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

          <section>
            <OperatorTabs loading={snapshot.loading} count={snapshotData} />
          </section>
        </header>

        <Routes>
          <Route
            path="*"
            element={
              <TicketSources year={years.selected} snapshot={snapshotData} />
            }
          />
        </Routes>
      </Main>
    </ImportArea>
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

export default Saf
