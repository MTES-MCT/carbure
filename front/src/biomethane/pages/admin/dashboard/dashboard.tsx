import { usePrivateNavigation } from "common/layouts/navigation"
import { useTranslation } from "react-i18next"
import { getBiomethaneAdminDashboard } from "../api"
import {
  useGetDashboardFilterOptions,
  useDashboardColumns,
} from "./dashboard.hooks"
import { useQuery } from "common/hooks/async"
import { Table } from "common/components/table2"
import { NoResult } from "common/components/no-result2"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import { useQueryBuilder } from "common/hooks/query-builder-2"
import { BiomethaneAdminDashboardQueryBuilder } from "../types"
import { Pagination } from "common/components/pagination2"
import { Content, Main } from "common/components/scaffold"
import { useRoutes } from "common/hooks/routes"

const currentYear = new Date().getFullYear()

const Dashboard = () => {
  const { t } = useTranslation()
  usePrivateNavigation(t("Tableau de bord"))
  const columns = useDashboardColumns()
  const routes = useRoutes()
  const { state, actions, query } = useQueryBuilder<
    BiomethaneAdminDashboardQueryBuilder["config"]
  >({
    year: currentYear,
  })

  const { getFilterOptions, filterLabels, normalizers } =
    useGetDashboardFilterOptions(query)

  const { result: dashboardData, loading } = useQuery(
    getBiomethaneAdminDashboard,
    {
      key: "biomethane-admin-dashboard",
      params: [query],
    }
  )

  return (
    <Main>
      <Content>
        <FilterMultiSelect2
          filterLabels={filterLabels}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={getFilterOptions}
          normalizers={normalizers}
        />
        {!loading && (!dashboardData || dashboardData?.count === 0) && (
          <NoResult />
        )}
        {dashboardData && dashboardData.count > 0 && (
          <>
            <Table
              rows={dashboardData.results ?? []}
              columns={columns}
              loading={loading}
              rowLink={(row) => ({
                pathname: routes
                  .BIOMETHANE(row.year)
                  .ADMIN.DECLARATION_DETAIL(row.producer.id).ROOT,
              })}
            />
            <Pagination
              defaultPage={query.page}
              total={dashboardData.count}
              limit={state.limit}
              onLimit={actions.setLimit}
              disabled={loading}
            />
          </>
        )}
      </Content>
    </Main>
  )
}

export default Dashboard
