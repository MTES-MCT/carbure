import { Content, Main } from "common/components/scaffold"
import useYears from "common/hooks/years-2"
import { usePrivateNavigation } from "common/layouts/navigation"
import { useTranslation } from "react-i18next"
import * as api from "./api"
import { Select } from "common/components/selects2"
import useEntity from "common/hooks/entity"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import { useQueryBuilder } from "common/hooks/query-builder-2"
import { useQuery } from "common/hooks/async"
import { ActionFilter, ActionQueryBuilder } from "h2/types"
import { ActionTable } from "./components/action-table"

const LotsPage = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  usePrivateNavigation(t("Lots"))

  const years = useYears("lots", () => api.getActionYears(entity.id))

  const { state, actions, query } =
    useQueryBuilder<ActionQueryBuilder["config"]>()

  const { result, loading } = useQuery(api.getActions, {
    key: "action-list",
    params: [query],
  })

  function getActionFilters(filter: ActionFilter) {
    return api.getActionFilters(filter, query)
  }

  return (
    <Main>
      <Select
        options={years.options}
        value={years.selected}
        onChange={years.setYear}
      />

      <Content marginTop>
        <FilterMultiSelect2
          filterLabels={{
            material: t("Matière"),
            shipping_method: t("Mode de transport"),
            site: t("Site"),
          }}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={getActionFilters}
        />

        <ActionTable
          actions={result?.data?.results ?? []}
          loading={loading}
          order={state.order}
          onOrder={actions.setOrder}
        />
      </Content>
    </Main>
  )
}

export default LotsPage
