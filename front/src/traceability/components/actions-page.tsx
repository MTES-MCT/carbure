import { ReactNode, useCallback, useMemo } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { isEmpty } from "ramda"

import HashRoute from "common/components/hash-route"
import { ActionBar, Content, Main } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import { Table } from "common/components/table2"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useQueryBuilder } from "common/hooks/query-builder-2"
import useYears from "common/hooks/years-2"
import { usePrivateNavigation } from "common/layouts/navigation"
import { Tabs } from "common/components/tabs2"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"

import { getActionFilters, getActions, getActionYears } from "traceability/api"
import {
  Action,
  ActionFilter,
  ActionIndustry,
  ActionQuery,
  ActionQueryBuilder,
} from "traceability/types"
import { ActionFilterDisplay } from "traceability/hooks/use-action-filters"
import { ActionColumn } from "traceability/hooks/action-columns"
import { useCombinedQuery } from "traceability/hooks/use-combined-query"
import { ActionTab, useActionTabs } from "traceability/hooks/use-action-tabs"
import { ActionModal } from "traceability/components/action-modal"
import { ActionExcelImportDialog } from "traceability/components/action-excel-import-dialog"
import { ActionFieldset } from "traceability/hooks/action-fields"
import { Button } from "common/components/button2"
import { FrIconClassName } from "@codegouvfr/react-dsfr"
import { SearchInput } from "common/components/inputs2"
import { Pagination } from "common/components/pagination2"

export const QUERY_KEY = "traceability-actions"

export type MainAction = {
  icon: FrIconClassName
  label: string
  onAction: () => void
}

export type ExcelImportConfig = {
  buttonLabel: string
  description: ReactNode

  // Temporary attribute to add labels to the fields of the excel import that are not stored on the Action model (ex: lot_id, batch_id, etc..)
  fieldLabels?: Record<string, string>
}

export type { ActionTab }

export type ActionsPageProps = {
  listTitle: string
  detailTitle: string
  subpath: string
  fixedQuery: Partial<ActionQuery>
  tabs?: ActionTab[]
  mainAction?: MainAction
  renderDetailActions?: (action: Action) => ReactNode
  excelImport?: ExcelImportConfig
  filters: ActionFilterDisplay[]
  columns: ActionColumn[]
  fieldsets?: ActionFieldset[]
  industry: ActionIndustry
  emptyState?: ReactNode
}

export const ActionsPage = ({
  listTitle,
  detailTitle,
  subpath,
  fixedQuery,
  tabs,
  mainAction,
  renderDetailActions,
  excelImport,
  filters,
  columns,
  fieldsets,
  industry,
  emptyState,
}: ActionsPageProps) => {
  usePrivateNavigation(listTitle)

  const entity = useEntity()
  const location = useLocation()
  const navigate = useNavigate()
  const actionTabs = useActionTabs(tabs)
  const pageQuery = useMemo(
    () => ({ ...fixedQuery, ...actionTabs.query }),
    [fixedQuery, actionTabs.query]
  )

  const visibleColumns = columns.filter(
    (column) => column.condition?.(entity) ?? true
  )

  const visibleFilters = filters.filter(
    (filter) => filter.condition?.(entity) ?? true
  )

  const filterLabels = Object.fromEntries(
    visibleFilters.map((filter) => [filter.key, filter.label])
  ) as Partial<Record<ActionFilter, string>>

  const fieldLabels = {
    ...Object.fromEntries(
      (fieldsets ?? []).flatMap((fieldset) =>
        fieldset.fields.map((field) => [field.key, field.label])
      )
    ),
    ...excelImport?.fieldLabels,
  }

  const filterNormalizers = Object.fromEntries(
    visibleFilters
      .filter((filter) => filter.normalizer)
      .map((filter) => [filter.key, filter.normalizer])
  )

  const years = useYears(subpath, () =>
    getActionYears(entity.id, industry, fixedQuery)
  )

  const { state, actions, query } = useQueryBuilder<
    ActionQueryBuilder["config"]
  >({ year: years.selected })

  const combinedQuery = useCombinedQuery(pageQuery, query)

  const { result, loading } = useQuery(getActions, {
    key: QUERY_KEY,
    params: [industry, combinedQuery],
    // Only execute the query if there is an active tab to avoid fetching data for nothing.
    executeOnMount: !actionTabs.hasTabs || Boolean(actionTabs.activeTab),
  })

  const getFilterOptions = useCallback(
    (filter: ActionFilter) => getActionFilters(filter, industry, combinedQuery),
    [industry, combinedQuery]
  )

  if (actionTabs.redirect) return actionTabs.redirect

  const showEmptyState =
    Boolean(emptyState) &&
    !loading &&
    !state.search &&
    isEmpty(state.filters) &&
    (result?.data?.count ?? 0) === 0

  if (showEmptyState) {
    return emptyState
  }

  return (
    <Main>
      <header>
        <section>
          <Select
            options={years.options}
            value={years.selected}
            onChange={years.setYear}
          />

          {mainAction && (
            <Button
              asideX
              size="large"
              iconId={mainAction.icon}
              onClick={mainAction.onAction}
            >
              {mainAction.label}
            </Button>
          )}
        </section>
      </header>

      {actionTabs.hasTabs && (
        <Tabs
          keepSearch
          sticky
          focus={actionTabs.activeTab?.key}
          tabs={actionTabs.links ?? []}
        />
      )}

      <Content marginTop={!actionTabs.hasTabs}>
        <ActionBar>
          <ActionBar.Grow>
            <SearchInput value={state.search} onChange={actions.setSearch} />
          </ActionBar.Grow>

          {excelImport && (
            <Button
              iconId="fr-icon-add-line"
              disabled={!entity.canWrite()}
              onClick={() =>
                navigate({ search: location.search, hash: "import" })
              }
            >
              {excelImport.buttonLabel}
            </Button>
          )}
        </ActionBar>

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
        <Pagination
          defaultPage={query.page}
          total={result?.data?.count ?? 0}
          limit={state.limit}
          onLimit={actions.setLimit}
        />
      </Content>

      {excelImport && entity.canWrite() && (
        <HashRoute
          path="import"
          element={
            <ActionExcelImportDialog
              description={excelImport.description}
              industry={industry}
              fieldLabels={fieldLabels}
            />
          }
        />
      )}

      {fieldsets && (
        <HashRoute
          path="action/:id"
          element={
            <ActionModal
              title={detailTitle}
              fieldsets={fieldsets}
              renderDetailActions={renderDetailActions}
              industry={industry}
            />
          }
        />
      )}
    </Main>
  )
}
