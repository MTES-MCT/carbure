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

  ELEC: (entity_id: number, year: number) => {
    const baseUrl = urlWithOrgId(entity_id, `/elec/${year}`)

    return {
      CERTIFICATES: `${baseUrl}/certificates`,
      PROVISIONNED_ENERGY: `${baseUrl}/provisioned`,
      TRANSFERRED_ENERGY: `${baseUrl}/transferred`,
      CHARGE_POINTS: {
        PENDING: `${baseUrl}/charge-points/pending`,
        METER_READINGS: `${baseUrl}/charge-points/meter-readings`,
        LIST: `${baseUrl}/charge-points/list`,
      },
    }
  },
  SAF: (entity_id: number, year: number) => {
    const baseUrl = urlWithOrgId(entity_id, `/saf/${year}`)

    return {
      TICKET_SOURCES: `${baseUrl}/ticket-sources`,
      TICKETS_RECEIVED: `${baseUrl}/tickets-received`,
      TICKETS: `${baseUrl}/tickets`,
      TICKETS_PENDING: `${baseUrl}/tickets/pending`,
      TICKETS_ACCEPTED: `${baseUrl}/tickets/accepted`,
    }
  },

  SETTINGS: (entity_id: number) => urlWithOrgId(entity_id, "/settings"),

  USER_GUIDE: "https://carbure-1.gitbook.io/faq",

  MY_ACCOUNT: "/account",
  LOGOUT: "/auth/logout",
  STATISTICS: (entity_id: number) => urlWithOrgId(entity_id, "/stats"),
  REGISTRY: (entity_id: number) => urlWithOrgId(entity_id, "/registry"),
}
