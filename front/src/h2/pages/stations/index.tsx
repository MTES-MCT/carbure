import { LoaderOverlay, Main } from "common/components/scaffold"
import { usePrivateNavigation } from "common/layouts/navigation"
import { useTranslation } from "react-i18next"
import { EmptyStations } from "./empty-stations"
import { getStations } from "./api"
import useEntity from "common/hooks/entity"
import { useQuery } from "common/hooks/async"

const StationsPage = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  usePrivateNavigation(t("Mes stations"))

  const { result, loading } = useQuery(getStations, {
    key: "h2-stations",
    params: [entity.id],
  })

  const stations = result?.data?.results ?? []
  const hasStations = stations.length > 0

  if (loading) {
    return <LoaderOverlay />
  }

  return <Main>{hasStations ? null : <EmptyStations />}</Main>
}

export default StationsPage
