import useEntity from "carbure/hooks/entity"
import { ROUTE_URLS } from "common/utils/routes"

/**
 * Prepare the routes with custom logic to avoid using same parameters multiple times
 */
export const useRoutes = () => {
  const entity = useEntity()
  const currentYear = new Date().getFullYear()

  const routes = {
    ...ROUTE_URLS,

    ORG: () => ROUTE_URLS.ORG(entity.id),

    ADMIN_COMPANY_DETAIL: (company_id: number) =>
      ROUTE_URLS.ADMIN_COMPANY_DETAIL(entity.id, company_id),

    BIOFUELS: (year: number = currentYear) =>
      ROUTE_URLS.BIOFUELS(entity.id, year),
    BIOFUELS_CONTROLS: (year: number = currentYear) =>
      ROUTE_URLS.BIOFUELS_CONTROLS(entity.id, year),

    ELEC: (year: number = currentYear) => ROUTE_URLS.ELEC(entity.id, year),
    ELEC_ADMIN: (year: number = currentYear) =>
      ROUTE_URLS.ELEC_ADMIN(entity.id, year),
    ELEC_AUDITOR: (year: number = currentYear) =>
      ROUTE_URLS.ELEC_AUDITOR(entity.id, year),

    SAF: (year: number = currentYear) => ROUTE_URLS.SAF(entity.id, year),

    SETTINGS: ROUTE_URLS.SETTINGS(entity.id),
    STATISTICS: ROUTE_URLS.STATISTICS(entity.id),
    REGISTRY: ROUTE_URLS.REGISTRY(entity.id),
  }

  return routes
}
