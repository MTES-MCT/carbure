const urlWithOrgId = (entity_id: number, url: string = "") =>
  `/org/${entity_id}${url}`

export const ROUTE_URLS = {
  ORG: (entity_id: number) => `/org/${entity_id}`,
  // Admin
  ADMIN: (entity_id: number) => {
    const baseUrl = urlWithOrgId(entity_id)

    return {
      DASHBOARD: `${baseUrl}/dashboard`,
      // Company detail page when the entity is admin
      COMPANY_DETAIL: (company_id: number) =>
        `${baseUrl}/entities/${company_id}`,
      DOUBLE_COUNT: {
        APPLICATIONS: `${baseUrl}/double-counting/applications`,
        AGREEMENTS: `${baseUrl}/double-counting/agreements`,
      },
      COMPANIES: `${baseUrl}/entities`,
    }
  },
  MATERIAL_ACCOUNTING: (entity_id: number) => {
    const baseUrl = urlWithOrgId(entity_id, "/accounting")

    return {
      OPERATIONS: `${baseUrl}/operations`,
      BALANCE: `${baseUrl}/balance`,
    }
  },

  BIOFUELS: (entity_id: number, year: number) => {
    const baseUrl = urlWithOrgId(entity_id, `/transactions/${year}`)

    return {
      DRAFT: `${baseUrl}/drafts`,
      RECEIVED: `${baseUrl}/in`,
      STOCKS: `${baseUrl}/stocks`,
      SENT: `${baseUrl}/out`,
    }
  },
  BIOFUELS_CONTROLS: (entity_id: number, year: number) => {
    const baseUrl = urlWithOrgId(entity_id, `/controls/${year}`)

    return {
      ALERTS: `${baseUrl}/alerts`,
      LOTS: `${baseUrl}/lots`,
      STOCKS: `${baseUrl}/stocks`,
    }
  },

  ELEC: (entity_id: number, year: number) => {
    const baseUrl = urlWithOrgId(entity_id, `/elec/${year}`)

    return {
      CERTIFICATES: `${baseUrl}/pending`,
      PROVISIONNED_ENERGY: `${baseUrl}/provisioned`,
      TRANSFERRED_ENERGY: `${baseUrl}/transferred`,
      CHARGE_POINTS: {
        PENDING: urlWithOrgId(entity_id, "/charge-points/applications"),
        METER_READINGS: urlWithOrgId(
          entity_id,
          "/charge-points/meter-readings"
        ),
        LIST: urlWithOrgId(entity_id, "/charge-points/list"),
      },
    }
  },
  ELEC_ADMIN: (entity_id: number, year: number) => {
    const baseUrl = urlWithOrgId(entity_id, `/elec-admin/${year}`)
    const baseChargePointsUrl = urlWithOrgId(
      entity_id,
      `/elec-admin-audit/${year}`
    )

    return {
      PROVISION: `${baseUrl}/provision`,
      TRANSFER: `${baseUrl}/transfer`,
      CHARGE_POINTS: {
        PENDING: `${baseChargePointsUrl}/charge-points`,
        METER_READINGS: `${baseChargePointsUrl}/meter-readings`,
      },
    }
  },
  ELEC_AUDITOR: (entity_id: number, year: number) =>
    urlWithOrgId(entity_id, `/elec-audit/${year}`),

  SAF: (entity_id: number, year: number) => {
    const baseUrl = urlWithOrgId(entity_id, `/saf/${year}`)

    return {
      TICKET_SOURCES: `${baseUrl}/ticket-sources`,
      TICKETS_RECEIVED: `${baseUrl}/tickets-received`,
      TICKETS_ASSIGNED: `${baseUrl}/tickets-assigned`,
      TICKETS: `${baseUrl}/tickets`,
      TICKETS_PENDING: `${baseUrl}/tickets/pending`,
      TICKETS_ACCEPTED: `${baseUrl}/tickets/accepted`,
    }
  },

  SETTINGS: (entity_id: number) => urlWithOrgId(entity_id, "/settings"),

  USER_GUIDE: "https://carbure-1.gitbook.io/faq",

  MY_ACCOUNT: {
    INDEX: "/account",
    ADD_COMPANY: "/account/add-company",
  },
  LOGOUT: "/auth/logout",
  STATISTICS: (entity_id: number) => urlWithOrgId(entity_id, "/stats"),
  REGISTRY: (entity_id: number) => urlWithOrgId(entity_id, "/registry"),

  HOME: "/",
  CONTACT: "/contact",
}
