import { useTranslation } from "react-i18next"
import { Cell, Column } from "common/components/table2"
import { apiTypes } from "common/services/api-fetch.types"
import { EntityType, UserRole } from "common/types"
import * as api from "../../api"
import {
  getEntityTypeLabel,
  getUserRoleLabel,
  normalizeBoolean,
} from "common/utils/normalizers"
import { AdminUserQuery, AdminUserQueryFilter } from "companies-admin/types"

export type AdminUserRow = apiTypes["AdminUserRow"]
export type AdminUserFilter = "entity_type" | "role" | "is_active"

export function useAdminUserFilters() {
  const { t } = useTranslation()

  return {
    entity_type: t("Type d'entité"),
    role: t("Rôle"),
    is_active: t("Utilisateur actif"),
  }
}

export function getAdminUserFilterOptions(
  filter: AdminUserQueryFilter,
  query: AdminUserQuery
) {
  return api.getAdminUsersFilters(filter, query)
}

export const adminUserFilterNormalizers = {
  entity_type: (type: EntityType) => ({
    value: type,
    label: getEntityTypeLabel(type),
  }),
  role: (role: UserRole) => ({
    value: role,
    label: getUserRoleLabel(role),
  }),
  is_active: normalizeBoolean,
}

export function useAdminUserColumns(): Column<AdminUserRow>[] {
  const { t } = useTranslation()

  return [
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
      key: "entity_id",
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
  ]
}
