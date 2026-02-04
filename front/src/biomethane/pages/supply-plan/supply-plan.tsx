import { Button } from "common/components/button2"
import { SearchInput } from "common/components/inputs2"
import { ActionBar } from "common/components/scaffold"
import { usePrivateNavigation } from "common/layouts/navigation"
import { useTranslation } from "react-i18next"
import { getSupplyPlanInputs, downloadSupplyPlan } from "./api"
import { useGetFilterOptions, useSupplyPlanColumns } from "./supply-plan.hooks"
import { useQuery } from "common/hooks/async"
import { Table } from "common/components/table2"
import { NoResult } from "common/components/no-result2"
import { RecapQuantity } from "common/molecules/recap-quantity"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import { useQueryBuilder } from "common/hooks/query-builder-2"
import { BiomethaneSupplyInputQueryBuilder } from "./types"
import { Pagination } from "common/components/pagination2"
import HashRoute from "common/components/hash-route"
import {
  CreateSupplyInputDialog,
  SupplyInputDialog,
} from "./supply-input-dialog"
import { ExportButton } from "common/components/export"
import { ExcelImportDialog } from "./supply-excel-import-dialog"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { useLocation, useNavigate } from "react-router-dom"
import { useRoutes } from "common/hooks/routes"
import { MissingFields } from "biomethane/components/missing-fields"
import { useSelectedEntity } from "common/providers/selected-entity-provider"

export const SupplyPlan = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const routes = useRoutes()
  usePrivateNavigation(t("Plan d'approvisionnement"))
  const { selectedYear, canEditDeclaration } = useAnnualDeclaration()
  const columns = useSupplyPlanColumns()
  const { selectedEntityId, hasSelectedEntity } = useSelectedEntity()

  const { state, actions, query } = useQueryBuilder<
    BiomethaneSupplyInputQueryBuilder["config"]
  >({
    year: selectedYear,
  })
  const { getFilterOptions, filterLabels, normalizers } =
    useGetFilterOptions(query)

  const { result: supplyInputs, loading } = useQuery(getSupplyPlanInputs, {
    key: `supply-plan-inputs`,
    params: [query, selectedEntityId],
  })

  const onClose = () => {
    navigate({ search: location.search, hash: "#" })
  }

  return (
    <>
      <MissingFields />
      {!hasSelectedEntity && (
        <Button
          onClick={() =>
            navigate(
              routes.BIOMETHANE(selectedYear).PRODUCER.SUPPLY_PLAN_IMPORT
            )
          }
          iconId="ri-upload-line"
          disabled={!canEditDeclaration}
          asideX
        >
          {t("Charger un plan d'approvisionnement")}
        </Button>
      )}

      <ActionBar>
        <ActionBar.Grow>
          <SearchInput value={state.search} onChange={actions.setSearch} />
        </ActionBar.Grow>
        {!hasSelectedEntity && (
          <Button
            onClick={() =>
              navigate(
                routes.BIOMETHANE(selectedYear).PRODUCER.SUPPLY_PLAN_ADD_INPUT
              )
            }
            iconId="ri-add-line"
            asideX
            priority="secondary"
            disabled={!canEditDeclaration}
          >
            {t("Ajouter un intrant")}
          </Button>
        )}
        <ExportButton
          query={query}
          download={(query) => downloadSupplyPlan(query, selectedEntityId)}
        />
      </ActionBar>
      <FilterMultiSelect2
        filterLabels={filterLabels}
        selected={state.filters}
        onSelect={actions.setFilters}
        getFilterOptions={getFilterOptions}
        normalizers={normalizers}
      />
      {!loading && (!supplyInputs || supplyInputs?.count === 0) && <NoResult />}
      {supplyInputs && supplyInputs.count > 0 && (
        <>
          <RecapQuantity
            text={t("{{total}} tonnes annuelles", {
              total: supplyInputs.annual_volumes_in_t,
            })}
          />
          <Table
            rows={supplyInputs?.results ?? []}
            columns={columns}
            loading={loading}
            rowLink={(row) => ({
              pathname: location.pathname,
              search: location.search,
              hash: `supply-input/${row.id}`,
            })}
          />
        </>
      )}

      {supplyInputs && supplyInputs.count > 0 && (
        <Pagination
          defaultPage={query.page}
          total={supplyInputs.count}
          limit={state.limit}
          onLimit={actions.setLimit}
          disabled={loading}
        />
      )}
      <HashRoute path="/supply-input/:id" element={<SupplyInputDialog />} />
      <HashRoute
        path="/import"
        element={<ExcelImportDialog onClose={onClose} />}
      />
      <HashRoute
        path="/create"
        element={<CreateSupplyInputDialog onClose={onClose} />}
      />
    </>
  )
}
