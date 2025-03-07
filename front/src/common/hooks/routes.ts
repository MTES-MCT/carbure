import useEntity from "carbure/hooks/entity"
import { ROUTE_URLS } from "common/utils/routes"

const currentYear = new Date().getFullYear()

/**
 * Prepare the routes with custom logic to avoid using same parameters multiple times
 */
export const useRoutes = () => {
  const entity = useEntity()

  const routes = {
    ...ROUTE_URLS,

    ORG: () => ROUTE_URLS.ORG(entity.id),

    ADMIN: () => ROUTE_URLS.ADMIN(entity.id),

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
    CONTACT: entity.name
      ? `${ROUTE_URLS.CONTACT}?company=${entity.name}`
      : ROUTE_URLS.CONTACT,

    MATERIAL_ACCOUNTING: ROUTE_URLS.MATERIAL_ACCOUNTING(entity.id),
  }

  return routes
}
