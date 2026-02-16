import { useSupplyPlanQuery } from "biomethane/pages/supply-plan/supply-plan.hooks"
import { useAnnualDeclarationYear } from "biomethane/providers/annual-declaration"

import { usePrivateNavigation } from "common/layouts/navigation"
import { useTranslation } from "react-i18next"
import { declarationInterval } from "biomethane/utils"
import { ActionBar, Content, Main } from "common/components/scaffold"
import { SearchInput } from "common/components/inputs2"
import { DownloadSupplyPlan } from "biomethane/pages/supply-plan/components/download-supply-plan"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import { SupplyPlanTable } from "biomethane/pages/supply-plan/components/supply-plan-table"
import { Select } from "common/components/selects2"
import { useAnnualDeclarationYearsAdmin } from "../hooks/use-annual-declaration-years-admin"
import { Tabs } from "common/components/tabs2"
import { useMemo } from "react"
import { useRoutes } from "common/hooks/routes"
import {
  useGetFiltersOptionsAdmin,
  useSupplyInputsColumnsAdmin,
} from "./supply-inputs.hooks"

export const SupplyInputsAdminPage = () => {
  const { t } = useTranslation()
  const years = useAnnualDeclarationYearsAdmin()
  const selectedYear = useAnnualDeclarationYear()
  const routes = useRoutes()
  usePrivateNavigation(t("Plan d'approvisionnement"))

  const year = selectedYear ?? declarationInterval.year

  const { queryBuilder, supplyPlan } = useSupplyPlanQuery(year)
  const filterOptions = useGetFiltersOptionsAdmin(queryBuilder.query)
  const columns = useSupplyInputsColumnsAdmin()

  const tabs = useMemo(
    () => [
      {
        key: "supply-inputs",
        label: t("Toutes les installations"),
        path: routes.BIOMETHANE(year).ADMIN.SUPPLY_INPUTS,
      },
    ],
    [t, year, routes]
  )

  return (
    <Main>
      <Select
        options={years.options}
        value={selectedYear}
        onChange={years.setYear}
      />
      <Tabs tabs={tabs} />
      <Content>
        <ActionBar>
          <ActionBar.Grow>
            <SearchInput
              value={queryBuilder.state.search}
              onChange={queryBuilder.actions.setSearch}
            />
          </ActionBar.Grow>
          <DownloadSupplyPlan query={queryBuilder.query} />
        </ActionBar>

        <FilterMultiSelect2
          filterLabels={filterOptions.filterLabels}
          selected={queryBuilder.state.filters}
          onSelect={queryBuilder.actions.setFilters}
          getFilterOptions={filterOptions.getFilterOptions}
          normalizers={filterOptions.normalizers}
        />
        <SupplyPlanTable
          supplyPlan={supplyPlan}
          queryBuilder={queryBuilder}
          columns={columns}
        />
      </Content>
    </Main>
  )
}
