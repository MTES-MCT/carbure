import useEntity from "carbure/hooks/entity"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import {
  useCBQueryBuilder,
  useCBQueryParamsStore,
} from "common/hooks/query-builder"
import FilterMultiSelect from "common/molecules/filter-select"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import * as api from "./api"
import { useStatus } from "./index.hooks"
import { StatusSwitcher } from "./status-switcher"
import { ChargePointFilter } from "./types"

type ChargePointsListProps = {
  year: number
}

const ChargePointsList = ({ year }: ChargePointsListProps) => {
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
  const applicationsResponse = useQuery(api.getChargePointsList, {
    key: "charge-points-list",
    params: [query],
  })

  const applications = applicationsResponse.result?.data.data ?? []

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
          <StatusSwitcher status={status} onSwitch={actions.setStatus} />
        </ActionBar>
      </section>
    </>
  )
}

export default ChargePointsList
