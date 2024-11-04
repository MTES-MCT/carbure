export const ROUTE_URLS = {
  // Admin

  // Company detail page when the entity is admin
  ADMIN_COMPANY_DETAIL: (entity_id: number, company_id: number) =>
    `/org/${entity_id}/entities/${company_id}`,
}
