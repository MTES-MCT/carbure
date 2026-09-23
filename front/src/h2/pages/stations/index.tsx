import { ActionBar, Content, Main } from "common/components/scaffold"
import { usePrivateNavigation } from "common/layouts/navigation"
import { useTranslation } from "react-i18next"
import { EmptyStations } from "./components/empty-stations"
import * as api from "./api"
import { useQuery } from "common/hooks/async"
import { useH2Permissions } from "h2/hooks/use-h2-permissions"
import { StationTable } from "./components/station-table"
import { Button } from "common/components/button2"
import { useCreateStationDialog } from "./components/create-station-dialog"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import { SearchInput } from "common/components/inputs2"
import { useQueryBuilder } from "common/hooks/query-builder-2"
import { H2StationFilter, H2StationsQueryBuilder } from "h2/types"
import { isEmpty } from "ramda"
import { normalizeBoolean } from "common/utils/normalizers"
import { normalizeAccessType } from "h2/utils/normalizers"

const StationsPage = () => {
  const { t } = useTranslation()
  const { canAccessAdmin, canWriteStations } = useH2Permissions()
  usePrivateNavigation(canAccessAdmin ? t("Stations") : t("Mes stations"))

  const openCreateStationDialog = useCreateStationDialog()

  const { state, actions, query } =
    useQueryBuilder<H2StationsQueryBuilder["config"]>()

  const { result, loading } = useQuery(api.getH2Stations, {
    key: "h2-stations",
    params: [query],
  })

  const stations = result?.data?.results ?? []
  const hasStations = (result?.data?.total_count ?? 0) > 0

  function getH2StationsFilters(filter: H2StationFilter) {
    return api.getH2StationsFilters(filter, query)
  }

  if (!loading && !hasStations && isEmpty(state.filters)) {
    return <EmptyStations />
  }

  return (
    <Main>
      {canWriteStations && (
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
      )}

      <Content marginTop={canWriteStations}>
        <ActionBar>
          <ActionBar.Grow>
            <SearchInput
              debounce={250}
              value={state.search}
              onChange={actions.setSearch}
            />
          </ActionBar.Grow>
        </ActionBar>

        <FilterMultiSelect2
          filterLabels={{
            access_type: t("Nature du site"),
            has_personal_vehicle_connector: t("Compatible VP"),
            commissioning_year: t("Mise en service"),
          }}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={getH2StationsFilters}
          normalizers={{
            access_type: normalizeAccessType,
            has_personal_vehicle_connector: normalizeBoolean,
          }}
        />

        <StationTable
          loading={loading}
          stations={stations}
          order={state.order}
          onOrder={actions.setOrder}
        />
      </Content>
    </Main>
  )
}

export default StationsPage
