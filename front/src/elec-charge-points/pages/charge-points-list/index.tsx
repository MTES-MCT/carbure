import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import { Download } from "common/components/icons"
import { SearchInput } from "common/components/input"
import { ActionBar, Bar } from "common/components/scaffold"
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
import { ChargePointFilter } from "./types"

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
  const chargePointsListResponse = useQuery(api.getChargePointsList, {
    key: "charge-points-list",
    params: [query],
  })

  const chargePointsListPagination = chargePointsListResponse.result?.data.data
  const chargePointsCount = chargePointsListPagination?.charge_points_list
    ? chargePointsListPagination?.charge_points_list.length
    : 0

  const filterLabels = useMemo(
    () => ({
      [ChargePointFilter.ValidationDate]: t("Date d'ajout"),
      [ChargePointFilter.ChargePointId]: t("Identifiant PDC"),
      [ChargePointFilter.StationId]: t("Dernier index - kWh"),
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
            <Button
              icon={Download}
              label={t("Exporter")}
              action={() => {}}
              asideX
            />
          )}
        </ActionBar>
        {chargePointsListPagination?.charge_points_list && (
          <ChargePointsListTable
            chargePoints={chargePointsListPagination?.charge_points_list}
            loading={chargePointsListResponse.loading}
            onOrder={actions.setOrder}
            order={state.order}
            onSelect={actions.setSelection}
            selected={state.selection}
            rowLink={() => ({
              pathname: "",
              search: "",
              hash: "",
            })}
          />
        )}
      </section>
    </>
  )
}

export default ChargePointsList
