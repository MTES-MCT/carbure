/**
 * TEMPORARY FIX
 * To simplify the migration between axios and the robust type checking with the backend,
 * some code will be duplicated, and removed after the migration ended.
 */
import useEntity from "common/hooks/entity"
import { useQuery } from "common/hooks/async"
import { useCallback, useEffect } from "react"
import { useLocation, useNavigate, useParams } from "react-router-dom"
import { FetchResponseType } from "common/services/api-fetch.types"
import { useYearsProvider } from "common/providers/years-provider"
import { useTranslation } from "react-i18next"

const currentYear = new Date().getFullYear()

function useYears(
  root: string,
  getYears: (entity_id: number) => Promise<FetchResponseType<number[]>>
) {
  const location = useLocation()
  const params = useParams<"year">()
  const navigate = useNavigate()
  const { t } = useTranslation()

  const entity = useEntity()
  const { setSelectedYear, setRoot } = useYearsProvider()

  const selected = parseInt(params.year ?? "") || currentYear

  // Setup the root of the page to change the selected year in the url for subpages
  useEffect(() => {
    setRoot(root)
  }, [root, setRoot])

  const setYear = useCallback(
    (year: number | undefined) => {
      const rx = new RegExp(`${root}/[0-9]+`)
      const replacement = `${root}/${year}`
      const pathname = location.pathname.replace(rx, replacement)
      navigate(pathname)
      setSelectedYear(year ?? currentYear)
    },
    [root, location, navigate, setSelectedYear]
  )

  const years = useQuery(getYears, {
    key: "years",
    params: [entity.id],

    // select the latest year if the selected one isn't available anymore
    onSuccess: (res) => {
      const years = listYears(res.data)
      if (!years.includes(selected)) {
        setYear(Math.max(...years))
      } else {
        setSelectedYear(selected)
      }
    },
  })

  return {
    loading: years.loading,
    options: listYears(years.result?.data).map((year) => ({
      label: `${t("Année")} ${year}`,
      value: year,
    })),
    selected,
    setYear,
  }
}

function listYears(years: number[] | undefined) {
  if (years?.length) return years
  else return [currentYear]
}

export default useYears
