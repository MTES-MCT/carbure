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
    ADMIN_COMPANY_DETAIL: (company_id: number) =>
      ROUTE_URLS.ADMIN_COMPANY_DETAIL(entity.id, company_id),
    BIOFUELS: (year: number = currentYear) =>
      ROUTE_URLS.BIOFUELS(entity.id, year),
    ELEC_CERTIFICATES: ROUTE_URLS.ELEC_CERTIFICATES(entity.id),
    SAF: (year: number = currentYear) => ROUTE_URLS.SAF(entity.id, year),
    SETTINGS: ROUTE_URLS.SETTINGS(entity.id),
  }

  return routes
}
