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
  ACCOUNTING: (entity_id: number) => {
    const baseUrl = urlWithOrgId(entity_id, "/accounting")

    return {
      OPERATIONS: {
        ROOT: `${baseUrl}/operations`,
        BIOFUELS: `${baseUrl}/operations/biofuels`,
        ELEC: `${baseUrl}/operations/elec`,
      },
      BALANCES: {
        ROOT: `${baseUrl}/balances`,
        BIOFUELS: `${baseUrl}/balances/biofuels`,
        ELEC: `${baseUrl}/balances/elec`,
      },
      TENEUR: `${baseUrl}/teneur`,
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

  BIOMETHANE: (entity_id: number, year?: number) => {
    const baseUrl = urlWithOrgId(entity_id, `/biomethane`)

    return {
      ROOT: `${baseUrl}`,
      SUPPLY_PLAN: year
        ? `${baseUrl}/${year}/supply-plan`
        : `${baseUrl}/supply-plan`,
      DIGESTATE: year ? `${baseUrl}/${year}/digestate` : `${baseUrl}/digestate`,
      ENERGY: year ? `${baseUrl}/${year}/energy` : `${baseUrl}/energy`,
    }
  },

  DOUBLE_COUNTING: (entity_id: number) => {
    const baseUrl = urlWithOrgId(entity_id, "/double-counting")

    return {
      AGREEMENTS: `${baseUrl}/agreements`,
    }
  },

  ELEC: (entity_id: number) => {
    return {
      CHARGE_POINTS: {
        PENDING: urlWithOrgId(entity_id, "/charge-points/applications"),
        METER_READINGS: urlWithOrgId(
          entity_id,
          "/charge-points/meter-readings"
        ),
        LIST: urlWithOrgId(entity_id, "/charge-points/list"),
        QUALICHARGE: urlWithOrgId(entity_id, "/charge-points/qualicharge"),
      },
    }
  },
  ELEC_ADMIN: (entity_id: number, year: number) => {
    const baseChargePointsUrl = urlWithOrgId(
      entity_id,
      `/elec-admin-audit/${year}`
    )

    return {
      CHARGE_POINTS: {
        PENDING: `${baseChargePointsUrl}/charge-points`,
        METER_READINGS: `${baseChargePointsUrl}/meter-readings`,
      },
    }
  },
  ELEC_AUDITOR: (entity_id: number, year: number) =>
    urlWithOrgId(entity_id, `/elec-audit/${year}`),

  ELEC_V2: (entity_id: number, year: number) => {
    const certURL = urlWithOrgId(entity_id, `/elec-v2/certificates/${year}`)
    return {
      CERTIFICATES: {
        PROVISION: `${certURL}/provision`,
        TRANSFER: `${certURL}/transfer`,
      },
    }
  },

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

  SETTINGS: (entity_id: number) => {
    const baseUrl = urlWithOrgId(entity_id, "/settings")

    return {
      ROOT: baseUrl,
      OPTIONS: `${baseUrl}/options`,
      INFO: `${baseUrl}/info`,
      CERTIFICATES: `${baseUrl}/certificates`,
      PRODUCTION: `${baseUrl}/production`,
      DEPOT: `${baseUrl}/depot`,
      USERS: `${baseUrl}/users`,
      BIOMETHANE: {
        CONTRACT: `${baseUrl}/biomethane/contract`,
        PRODUCTION: `${baseUrl}/biomethane/production`,
        INJECTION: `${baseUrl}/biomethane/injection`,
      },
    }
  },

  USER_GUIDE: "https://carbure-1.gitbook.io/faq",

  MY_ACCOUNT: {
    INDEX: "/account",
    IDENTIFIERS: "/account/identifiers",
    ADD_COMPANY: "/account/companies/add",
    COMPANIES: "/account/companies",
    COMPANY_REGISTRATION: "/account/companies/registration",
    FOREIGN_COMPANY_REGISTRATION: "/account/companies/registration/foreign",
  },
  AUTH: {
    LOGOUT: "/auth/logout",
    RESET_PASSWORD_REQUEST: "/auth/reset-password-request",
    ACTIVATE_REQUEST: "/auth/activate-request",
  },
  STATISTICS: (entity_id: number) => urlWithOrgId(entity_id, "/stats"),
  REGISTRY: (entity_id: number) => urlWithOrgId(entity_id, "/registry"),

  HOME: "/",
  CONTACT: "/contact",
  PUBLIC_STATS: "/stats",
}

/**
 * Adds query parameters to a URL
 * @param url - The base URL
 * @param params - An object containing the query parameters to add
 * @returns The URL with query parameters
 */
export const addQueryParams = (
  url: string,
  params: Record<
    string,
    string | number | boolean | string[] | number[] | undefined | null
  >,
  excludeEmptyValues: boolean = true
) => {
  // Separates the base URL from existing parameters
  const [baseUrl, existingQuery] = url.split("?")
  const searchParams = new URLSearchParams(existingQuery)

  // Adds new parameters
  Object.entries(params).forEach(([key, value]) => {
    if (
      excludeEmptyValues &&
      (value === null || value === undefined || value === "")
    )
      return

    // Array handling
    if (Array.isArray(value)) {
      // Filters empty values if excludeEmptyValues is true
      const filteredValues = excludeEmptyValues
        ? value.filter((v) => v !== null && v !== undefined && v !== "")
        : value

      // Adds each array value as a separate parameter
      filteredValues.forEach((item) => {
        searchParams.append(key, item?.toString() ?? "")
      })
    } else {
      // Simple value handling
      searchParams.append(key, value?.toString() ?? "")
    }
  })

  const queryString = searchParams.toString()
  return queryString
    ? `${baseUrl as string}?${queryString}`
    : (baseUrl as string)
}
