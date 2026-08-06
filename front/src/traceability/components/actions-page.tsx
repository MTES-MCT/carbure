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
import { Normalizer } from "common/utils/normalize"

import { getActionFilters, getActions, getActionYears } from "traceability/api"
import {
  Action,
  ActionFilter,
  ActionFixedQuery,
  ActionQueryBuilder,
} from "traceability/types"

import { ActionColumn, ActionLabelOverrides } from "./action-config"
import { useActionDisplay } from "./use-action-display"

export type ActionsPageProps = {
  title: string
  yearsRoot: string
  fixedQuery: ActionFixedQuery
  columns?: ActionColumn[]
  filters?: ActionFilter[]
  labels?: ActionLabelOverrides
  filterNormalizers?: Partial<Record<ActionFilter, Normalizer<unknown, string>>>
  queryKey?: string
  onRowAction?: (action: Action, index: number) => void
}

export const ActionsPage = ({
  title,
  yearsRoot,
  fixedQuery,
  columns,
  filters,
  labels,
  filterNormalizers,
  queryKey = "traceability-actions",
  onRowAction,
}: ActionsPageProps) => {
  usePrivateNavigation(title)

  const entity = useEntity()
  const { tableColumns, filterLabels } = useActionDisplay({
    columns,
    filters,
    labels,
  })

  const years = useYears(yearsRoot, () => getActionYears(entity.id, fixedQuery))

  const { state, actions, query } =
    useQueryBuilder<ActionQueryBuilder["config"]>()

  const { result, loading } = useQuery(getActions, {
    key: queryKey,
    params: [query, fixedQuery],
  })

  const getFilterOptions = useCallback(
    (filter: ActionFilter) => getActionFilters(filter, query, fixedQuery),
    [query, fixedQuery]
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
          columns={tableColumns}
          rows={result?.data?.results ?? []}
          order={state.order}
          onOrder={actions.setOrder}
          onAction={onRowAction}
        />
      </Content>
    </Main>
  )
}

export type { ActionColumn, ActionLabelOverrides } from "./action-config"
export { DEFAULT_ACTION_COLUMNS, DEFAULT_ACTION_FILTERS } from "./action-config"
