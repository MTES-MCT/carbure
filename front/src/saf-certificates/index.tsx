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
import HashRoute from "common/components/hash-route"
import { UserRole } from "carbure/types"
import useEntity from "carbure/hooks/entity"
import { useQuery } from "common/hooks/async"
import * as api from "./api"
import { Main } from "common/components/scaffold"
import Select from "common/components/select"
import StatusTabs from "./components/status"
import {
  DeclarationButton,
  DeclarationDialog,
} from "../transactions/actions/declaration"
import { ImportArea } from "../transactions/actions/import"
import Lots from "../transactions/components/lots"
import Stocks from "../transactions/components/stocks"
import { Certificates } from "./components/certificates"

export const SafCertificates = () => {
  const { t } = useTranslation()

  const entity = useEntity()

  const years = useYears("saf-certificates", api.getYears)

  const snapshot = useQuery(api.getSafSnapshot, {
    key: "snapshot",
    params: [entity.id, years.selected],
  })

  const snapshotData = snapshot.result?.data.data

  // common props for subroutes
  const props = { year: years.selected, snapshot: snapshotData }

  return (
    <ImportArea>
      <Main>
        <header>
          <section>
            <h1>{t("SAF")}</h1>

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
            <StatusTabs loading={snapshot.loading} count={snapshotData} />
          </section>
        </header>

        <Routes>
          {/* <Route path="*" element={<Certificates {...props} />} /> */}
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

export default SafCertificates
