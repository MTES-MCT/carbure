import { useCallback } from "react"

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
  Action,
  ActionFilter,
  ActionQuery,
  ActionQueryBuilder,
} from "traceability/types"
import { ActionFilterDisplay } from "traceability/hooks/use-action-filters"
import { ActionColumnDefinition } from "traceability/hooks/use-action-columns"
import { useCombinedQuery } from "traceability/hooks/use-combined-query"

export const QUERY_KEY = "traceability-actions"

export type ActionsPageProps = {
  title: string
  subpath: string
  fixedQuery: Partial<ActionQuery>
  columns: ActionColumnDefinition[]
  filters: ActionFilterDisplay[]
  onRowAction?: (action: Action, index: number) => void
}

export const ActionsPage = ({
  title,
  subpath,
  fixedQuery,
  columns,
  filters,
  onRowAction,
}: ActionsPageProps) => {
  usePrivateNavigation(title)

  const entity = useEntity()

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
          onAction={onRowAction}
        />
      </Content>
    </Main>
  )
}
