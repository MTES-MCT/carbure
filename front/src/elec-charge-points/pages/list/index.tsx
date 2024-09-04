import useEntity from "carbure/hooks/entity"
import Alert from "common/components/alert"
import Button from "common/components/button"
import { AlertCircle, Download, Loader } from "common/components/icons"
import { SearchInput } from "common/components/input"
import Pagination from "common/components/pagination"
import { ActionBar, Bar, LoaderOverlay } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import {
  useCBQueryBuilder,
  useCBQueryParamsStore,
} from "common/hooks/query-builder"
import FilterMultiSelect from "common/molecules/filter-select"
import { ChargePointsSnapshot } from "elec-charge-points/types"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import * as api from "./api"
import { useStatus } from "./index.hooks"
import { StatusSwitcher } from "./status-switcher"
import { ChargePointsListTable } from "./table"
import { ChargePointFilter, ChargePointStatus } from "./types"

type ChargePointsListProps = {
  year: number
  snapshot: ChargePointsSnapshot
}

const ChargePointsList = ({ year, snapshot }: ChargePointsListProps) => {
  const entity = useEntity()
  const { t } = useTranslation()
  const status = useStatus()

  // Check snapshot is useless (used anywhere)
  const [state, actions] = useCBQueryParamsStore(
    entity,
    year,
    status,
    undefined
  )

  const query = useCBQueryBuilder(state)
  console.log("le status", { query, status })
  const chargePointsListQuery = useQuery(api.getChargePointsList, {
    key: "charge-points-list",
    params: [query],
  })

  const chargePointsListPagination = chargePointsListQuery.result?.data.data
  const chargePointsList = chargePointsListPagination?.elec_charge_points || []
  const chargePointsCount = chargePointsListPagination?.elec_charge_points
    ? chargePointsListPagination?.elec_charge_points.length
    : 0

  const filterLabels = useMemo(
    () => ({
      // [ChargePointFilter.Status]: t("Status"),
      [ChargePointFilter.MeasureDate]: t("Date du dernier relevé"),
      [ChargePointFilter.ChargePointId]: t("Identifiant PDC"),
      [ChargePointFilter.StationId]: t("Identifiant station"),
      [ChargePointFilter.ConcernedByReadingMeter]: t("Relevé trimestriel"),
    }),
    [t]
  )

  return (
    <>
      <Bar>
        <FilterMultiSelect
          filterLabels={filterLabels}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={(filter) =>
            api.getChargePointsFilters(filter, query)
          }
        />
      </Bar>
      <section>
        <ActionBar>
          <StatusSwitcher
            status={status}
            onSwitch={actions.setStatus}
            snapshot={snapshot}
          />
          <SearchInput
            clear
            asideX
            debounce={250}
            value={state.search}
            onChange={actions.setSearch}
          />
          {chargePointsCount > 0 && (
            <Button icon={Download} label={t("Exporter")} action={() => {}} />
          )}
        </ActionBar>
        {chargePointsList.length > 0 && (
          <>
            <ChargePointsListTable
              chargePoints={chargePointsList}
              loading={chargePointsListQuery.loading}
              onOrder={actions.setOrder}
              order={state.order}
              onSelect={actions.setSelection}
              selected={state.selection}
            />
            <Pagination
              page={state.page}
              limit={state.limit}
              total={chargePointsListPagination?.total || 0}
              onPage={actions.setPage}
              onLimit={actions.setLimit}
            />
          </>
        )}

        {chargePointsListQuery.loading && chargePointsCount === 0 && (
          <Loader color="var(--black)" size={32} />
        )}

        {!chargePointsListQuery.loading && chargePointsCount === 0 && (
          <>
            <section>
              <Alert icon={AlertCircle} variant="warning">
                {t("Aucun point de recharge trouvé")}
              </Alert>
            </section>
            <footer />
          </>
        )}
      </section>
    </>
  )
}

export default ChargePointsList
