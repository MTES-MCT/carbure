import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import { OperationsFilter, OperationsStatus } from "./types"
import { useTranslation } from "react-i18next"
import {
  useCBQueryBuilder,
  useCBQueryParamsStore,
} from "common/hooks/query-builder-2"
import useEntity from "carbure/hooks/entity"
import * as api from "./api"

const currentYear = new Date().getFullYear()

export const Operations = () => {
  const { t } = useTranslation()
  const entity = useEntity()

  const filterLabels = {
    [OperationsFilter.statuses]: t("Statut"),
    [OperationsFilter.sectors]: t("Filière"),
    [OperationsFilter.categories]: t("Catégorie"),
    [OperationsFilter.biofuels]: t("Biocarburants"),
    [OperationsFilter.operations]: t("Opération"),
    [OperationsFilter.depots]: t("Dépôts"),
  }

  const [state, actions] = useCBQueryParamsStore<OperationsStatus, undefined>(
    entity,
    currentYear
  )

  const query = useCBQueryBuilder<[], OperationsStatus, undefined>(state)

  return (
    <>
      <FilterMultiSelect2
        filterLabels={filterLabels}
        selected={state.filters}
        onSelect={actions.setFilters}
        getFilterOptions={async (filter) => {
          const res = await api.getOperationsFilters(filter, query)
          return res.data ?? []
        }}
      />
    </>
  )
}
