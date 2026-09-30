import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Button } from "common/components/button2"
import { SearchInput } from "common/components/inputs2"
import { NoResult } from "common/components/no-result2"
import { Pagination } from "common/components/pagination2/pagination"
import { ActionBar, Content, Main } from "common/components/scaffold"
import { Table } from "common/components/table2"
import useEntity from "common/hooks/entity"
import { useQuery } from "common/hooks/async"
import { useQueryBuilder } from "common/hooks/query-builder-2"
import useTitle from "common/hooks/title"
import { usePrivateNavigation } from "common/layouts/navigation"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import { ROUTE_URLS } from "common/utils/routes"
import * as api from "../../api"
import { EntityIdsFilter } from "../../components/entity-ids-filter"
import {
  adminUserFilterNormalizers,
  getAdminUserFilterOptions,
  useAdminUserColumns,
  useAdminUserFilters,
} from "./hooks"
import {
  AdminUserQueryBuilder,
  AdminUserQueryFilter,
} from "companies-admin/types"

const AdminUsers = () => {
  const { t } = useTranslation()
  useTitle(t("Utilisateurs"))
  usePrivateNavigation(t("Utilisateurs"))
  const entity = useEntity()

  const { state, actions, query } =
    useQueryBuilder<AdminUserQueryBuilder["config"]>()
  const [entityIds, setEntityIds] = useState("")
  const filterLabels = useAdminUserFilters()
  const columns = useAdminUserColumns()

  const { result, loading } = useQuery(api.getAdminUsers, {
    key: "admin-users",
    params: [query, entityIds],
  })

  const rows = result?.data?.results ?? []
  const entityUsersPath = (entityId: number) =>
    `${ROUTE_URLS.ADMIN(entity.id).COMPANY_DETAIL(entityId)}#users`

  return (
    <Main>
      <Content>
        <ActionBar>
          <ActionBar.Grow>
            <SearchInput
              value={state.search}
              placeholder={t("Rechercher une adresse e-mail ou une entité")}
              onChange={actions.setSearch}
            />
          </ActionBar.Grow>
          <Button>Exporter</Button>
        </ActionBar>

        <FilterMultiSelect2
          filterLabels={filterLabels}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={(filter) =>
            getAdminUserFilterOptions(filter as AdminUserQueryFilter, query)
          }
          normalizers={adminUserFilterNormalizers}
        >
          <EntityIdsFilter
            value={entityIds}
            onChange={(nextEntityIds) => {
              setEntityIds(nextEntityIds)
              actions.setPage(1)
            }}
          />
        </FilterMultiSelect2>
        {!loading && rows.length === 0 ? (
          <NoResult filters={state.filters} onFilter={actions.setFilters} />
        ) : (
          <>
            <Table
              loading={loading}
              rows={rows}
              rowLink={(row) => entityUsersPath(row.entity_id)}
              columns={columns}
            />
            <Pagination
              defaultPage={query.page}
              total={result?.data?.count ?? 0}
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

export default AdminUsers
