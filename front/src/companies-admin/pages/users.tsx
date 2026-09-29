import { useState } from "react"
import { useTranslation } from "react-i18next"
import { SearchInput } from "common/components/inputs2"
import { NoResult } from "common/components/no-result2"
import { Pagination } from "common/components/pagination2/pagination"
import { ActionBar, Content, Main } from "common/components/scaffold"
import { Cell, Table } from "common/components/table2"
import useEntity from "common/hooks/entity"
import { useQuery } from "common/hooks/async"
import { useQueryBuilder } from "common/hooks/query-builder-2"
import useTitle from "common/hooks/title"
import { usePrivateNavigation } from "common/layouts/navigation"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import { QueryParams } from "common/services/api-fetch.types"
import { EntityType, UserRole } from "common/types"
import {
  getEntityTypeLabel,
  getUserRoleLabel,
  normalizeBoolean,
} from "common/utils/normalizers"
import { ROUTE_URLS } from "common/utils/routes"
import * as api from "../api"
import { EntityIdsFilter } from "../components/entity-ids-filter"
import { Button } from "common/components/button2"

const AdminUsers = () => {
  const { t } = useTranslation()
  useTitle(t("Utilisateurs"))
  usePrivateNavigation(t("Utilisateurs"))
  const entity = useEntity()

  const { state, actions, query } = useQueryBuilder()
  const listQuery = query as QueryParams<"/entities/admin-users/">
  const [entityIds, setEntityIds] = useState("")

  const { result, loading } = useQuery(api.getAdminUsers, {
    key: "admin-users",
    params: [listQuery, entityIds],
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

        <FilterMultiSelect2<"entity_type" | "role" | "is_active", string>
          filterLabels={{
            entity_type: t("Type d'entité"),
            role: t("Rôle"),
            is_active: t("Utilisateur actif"),
          }}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={getFilterOptions}
          normalizers={{
            entity_type: (type: EntityType) => ({
              value: type,
              label: getEntityTypeLabel(type),
            }),
            role: (role: UserRole) => ({
              value: role,
              label: getUserRoleLabel(role),
            }),
            is_active: normalizeBoolean,
          }}
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
              columns={[
                {
                  key: "entity",
                  header: t("Entité"),
                  cell: (row) => (
                    <Cell
                      text={row.entity_name}
                      sub={getEntityTypeLabel(row.entity_type)}
                    />
                  ),
                },
                {
                  key: "entity",
                  header: t("Entity id"),
                  cell: (row) => <Cell text={row.entity_id} />,
                },
                {
                  key: "id",
                  header: t("Utilisateur"),
                  cell: (row) => <Cell text={row.email} />,
                },

                {
                  small: true,
                  key: "role",
                  header: t("Rôle"),
                  cell: (row) => getUserRoleLabel(row.role),
                },
                {
                  small: true,
                  key: "is_active",
                  header: t("Actif"),
                  cell: (row) => (row.is_active ? t("Oui") : t("Non")),
                },
                {
                  small: true,
                  key: "actions",
                  header: t("Actions"),
                  cell: () => t("Consulter"),
                },
              ]}
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

function getFilterOptions(filter: "entity_type" | "role" | "is_active") {
  if (filter === "entity_type")
    return Promise.resolve(Object.values(EntityType))
  if (filter === "is_active") return Promise.resolve(["true", "false"])
  return Promise.resolve(Object.values(UserRole))
}

export default AdminUsers
