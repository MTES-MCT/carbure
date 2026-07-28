import { IconName } from "common/components/icon"
import { AccountingPermissions } from "accounting/permissions"
import { ROUTE_URLS } from "common/utils/routes"

type AccountingRoutes = ReturnType<typeof ROUTE_URLS.ACCOUNTING>

type CommonSidebarEntry = {
  titleKey: string
  icon: IconName
  iconActive: IconName
}
type SidebarEntry = CommonSidebarEntry & {
  path: (routes: AccountingRoutes) => string
  canAccess: (permissions: AccountingPermissions) => boolean
}

const OPERATION_NAV_ITEM: CommonSidebarEntry = {
  titleKey: "Opérations",
  icon: "ri-bar-chart-2-line",
  iconActive: "ri-bar-chart-2-fill",
}

const OBJECTIVE_NAV_ITEM: CommonSidebarEntry = {
  titleKey: "Objectifs annuels",
  icon: "ri-flashlight-line",
  iconActive: "ri-flashlight-fill",
}

/** Liable and admin both use objectives routes (/objectives vs /admin/objectives). */
export const ACCOUNTING_SIDEBAR_NAV = {
  liable: [
    {
      titleKey: "Soldes",
      icon: "ri-bank-line",
      iconActive: "ri-bank-fill",
      path: (routes) => routes.BALANCES.ROOT,
      canAccess: (permissions) => permissions.canAccessBalances,
    },
    {
      ...OPERATION_NAV_ITEM,
      path: (routes) => routes.OPERATIONS.ROOT,
      canAccess: (permissions) => permissions.canAccessOperations,
    },
    {
      ...OBJECTIVE_NAV_ITEM,
      path: (routes) => routes.OBJECTIVES.ROOT,
      canAccess: (permissions) => permissions.liable.canAccessObjectives,
    },
  ],
  admin: [
    {
      ...OPERATION_NAV_ITEM,
      path: (routes) => routes.ADMIN.OPERATIONS,
      canAccess: (permissions) =>
        permissions.adminPermissions.canAccessOperations,
    },
    {
      ...OBJECTIVE_NAV_ITEM,
      path: (routes) => routes.ADMIN.OBJECTIVES,
      canAccess: (permissions) =>
        permissions.adminPermissions.canAccessObjectives,
    },
  ],
} satisfies Record<"liable" | "admin", SidebarEntry[]>
