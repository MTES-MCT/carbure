const urlWithOrgId = (entity_id: number, url: string) =>
  `/org/${entity_id}${url}`

export const ROUTE_URLS = {
  // Admin

  // Company detail page when the entity is admin
  ADMIN_COMPANY_DETAIL: (entity_id: number, company_id: number) =>
    urlWithOrgId(entity_id, `/entities/${company_id}`),

  BIOFUELS: (entity_id: number, year: number) => {
    const baseUrl = urlWithOrgId(entity_id, `/transactions/${year}`)

    return {
      DRAFT: `${baseUrl}/drafts`,
      RECEIVED: `${baseUrl}/in`,
      STOCKS: `${baseUrl}/stocks`,
      SENT: `${baseUrl}/out`,
    }
  },

  ELEC_CERTIFICATES: (entity_id: number) => urlWithOrgId(entity_id, "/elec"),

  SAF: (entity_id: number, year: number) => {
    const baseUrl = urlWithOrgId(entity_id, `/saf/${year}`)

    return {
      TICKET_SOURCES: `${baseUrl}/ticket-sources`,
      TICKETS_RECEIVED: `${baseUrl}/received`,
      TICKETS_AFFECTED: `${baseUrl}/affected`,
    }
  },

  SETTINGS: (entity_id: number) => urlWithOrgId(entity_id, "/settings"),

  USER_GUIDE: "https://carbure-1.gitbook.io/faq",
}
