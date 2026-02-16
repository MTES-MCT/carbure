import { Button } from "common/components/button2"
import { SearchInput } from "common/components/inputs2"
import { ActionBar } from "common/components/scaffold"
import { usePrivateNavigation } from "common/layouts/navigation"
import { useTranslation } from "react-i18next"
import { useSupplyPlanQuery } from "./supply-plan.hooks"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import HashRoute from "common/components/hash-route"
import {
  CreateSupplyInputDialog,
  SupplyInputDialog,
} from "./supply-input-dialog"
import { ExcelImportDialog } from "./supply-excel-import-dialog"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { useLocation, useNavigate } from "react-router-dom"
import { useRoutes } from "common/hooks/routes"
import { MissingFields } from "biomethane/components/missing-fields"
import { useSelectedEntity } from "common/providers/selected-entity-provider"
import { DownloadSupplyPlan } from "./components/download-supply-plan"
import { SupplyPlanTable } from "./components/supply-plan-table"

export const SupplyPlan = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const routes = useRoutes()
  usePrivateNavigation(t("Plan d'approvisionnement"))
  const { selectedYear, canEditDeclaration } = useAnnualDeclaration()

  const { hasSelectedEntity } = useSelectedEntity()

  const { queryBuilder, filterOptions, supplyPlan } =
    useSupplyPlanQuery(selectedYear)

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
          <SearchInput
            value={queryBuilder.state.search}
            onChange={queryBuilder.actions.setSearch}
          />
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
        <DownloadSupplyPlan query={queryBuilder.query} />
      </ActionBar>
      <FilterMultiSelect2
        filterLabels={filterOptions.filterLabels}
        selected={queryBuilder.state.filters}
        onSelect={queryBuilder.actions.setFilters}
        getFilterOptions={filterOptions.getFilterOptions}
        normalizers={filterOptions.normalizers}
      />
      <SupplyPlanTable supplyPlan={supplyPlan} queryBuilder={queryBuilder} />
      <HashRoute
        path="/supply-input/:id"
        element={<SupplyInputDialog isReadOnly={!canEditDeclaration} />}
      />
      <HashRoute
        path="/import"
        element={
          <ExcelImportDialog
            onClose={() => {
              queryBuilder.actions.setFilters({})
              onClose()
            }}
          />
        }
      />
      <HashRoute
        path="/create"
        element={<CreateSupplyInputDialog onClose={onClose} />}
      />
    </>
  )
}
