import { Content, LoaderOverlay, Main } from "common/components/scaffold"
import { usePrivateNavigation } from "common/layouts/navigation"
import { useTranslation } from "react-i18next"
import { EmptyStations } from "./components/empty-stations"
import { getStations } from "./api"
import useEntity from "common/hooks/entity"
import { useQuery } from "common/hooks/async"
import { StationTable } from "./components/station-table"
import { Button } from "common/components/button2"
import { useCreateStationDialog } from "./components/create-station-dialog"

const StationsPage = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  usePrivateNavigation(t("Mes stations"))

  const openCreateStationDialog = useCreateStationDialog()

  const { result, loading } = useQuery(getStations, {
    key: "h2-stations",
    params: [entity.id],
  })

  const stations = result?.data?.results ?? []
  const hasStations = stations.length > 0

  if (!loading && !hasStations) {
    return <EmptyStations />
  }

  return (
    <Main>
      <header>
        <Button
          asideX
          size="large"
          iconId="ri-add-line"
          onClick={openCreateStationDialog}
        >
          {t("Ajouter une station")}
        </Button>
      </header>

      <Content marginTop>
        <StationTable stations={stations} />
      </Content>

      {loading && <LoaderOverlay />}
    </Main>
  )
}

export default StationsPage
