import useEntity from "carbure/hooks/entity"
import { ROUTE_URLS } from "common/utils/routes"

/**
 * Prepare the routes with custom logic to avoid using same parameters multiple times
 */
export const useRoutes = () => {
  const entity = useEntity()
  const currentYear = new Date().getFullYear()

  const routes: {
    [K in keyof typeof ROUTE_URLS]: (
      ...args: any[]
    ) => ReturnType<(typeof ROUTE_URLS)[K]>
  } = {
    ...ROUTE_URLS,
    ADMIN_COMPANY_DETAIL: (company_id: number) =>
      ROUTE_URLS.ADMIN_COMPANY_DETAIL(entity.id, company_id),
    BIOFUELS: (year: number = currentYear) =>
      ROUTE_URLS.BIOFUELS(entity.id, year),
  }

  return routes
}
