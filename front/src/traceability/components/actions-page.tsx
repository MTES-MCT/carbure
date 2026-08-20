import { useCallback } from "react"
import { useLocation } from "react-router-dom"

import HashRoute from "common/components/hash-route"
import { Content, Main } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import { Table } from "common/components/table2"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useQueryBuilder } from "common/hooks/query-builder-2"
import useYears from "common/hooks/years-2"
import { usePrivateNavigation } from "common/layouts/navigation"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"

import { getActionFilters, getActions, getActionYears } from "traceability/api"
import {
  ActionFilter,
  ActionQuery,
  ActionQueryBuilder,
} from "traceability/types"
import { ActionFilterDisplay } from "traceability/hooks/use-action-filters"
import { ActionColumn } from "traceability/hooks/use-action-columns"
import { useCombinedQuery } from "traceability/hooks/use-combined-query"
import { ActionModal } from "traceability/components/action-modal"
import { ActionField } from "traceability/hooks/use-action-fields"

export const QUERY_KEY = "traceability-actions"

export type ActionsPageProps = {
  listTitle: string
  detailTitle: string
  subpath: string
  fixedQuery: Partial<ActionQuery>
  columns: ActionColumn[]
  filters: ActionFilterDisplay[]
  fields?: ActionField[]
}

export const ActionsPage = ({
  listTitle,
  detailTitle,
  subpath,
  fixedQuery,
  columns,
  filters,
  fields,
}: ActionsPageProps) => {
  usePrivateNavigation(listTitle)

  const entity = useEntity()
  const location = useLocation()

  const visibleColumns = columns.filter(
    (column) => column.condition?.(entity) ?? true
  )

  const visibleFilters = filters.filter(
    (filter) => filter.condition?.(entity) ?? true
  )

  const filterLabels = Object.fromEntries(
    visibleFilters.map((filter) => [filter.key, filter.label])
  ) as Partial<Record<ActionFilter, string>>

  const filterNormalizers = Object.fromEntries(
    visibleFilters
      .filter((filter) => filter.normalizer)
      .map((filter) => [filter.key, filter.normalizer])
  )

  const years = useYears(subpath, () => getActionYears(entity.id, fixedQuery))

  const { state, actions, query } =
    useQueryBuilder<ActionQueryBuilder["config"]>()

  const combinedQuery = useCombinedQuery(fixedQuery, query)

  const { result, loading } = useQuery(getActions, {
    key: QUERY_KEY,
    params: [combinedQuery],
  })

  const getFilterOptions = useCallback(
    (filter: ActionFilter) => getActionFilters(filter, combinedQuery),
    [combinedQuery]
  )

  return (
    <Main>
      <Select
        options={years.options}
        value={years.selected}
        onChange={years.setYear}
      />

      <Content marginTop>
        <FilterMultiSelect2
          filterLabels={filterLabels}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={getFilterOptions}
          normalizers={filterNormalizers}
        />

        <Table
          loading={loading}
          columns={visibleColumns}
          rows={result?.data?.results ?? []}
          order={state.order}
          onOrder={actions.setOrder}
          rowLink={(action) => ({
            pathname: location.pathname,
            search: location.search,
            hash: `action/${action.id}`,
          })}
        />
      </Content>

      {fields && (
        <HashRoute
          path="action/:id"
          element={<ActionModal title={detailTitle} fields={fields} />}
        />
      )}
    </Main>
  )
}
