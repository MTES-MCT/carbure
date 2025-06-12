import { Api } from "common/services/api"
import { AxiosResponse } from "axios"
import { api as apiFetch } from "common/services/api-fetch"
import { EntityType } from "./types"

export function getUserSettings() {
  return apiFetch.GET("/user/")
}

export function extract<T>(res: AxiosResponse<Api<T[]>>) {
  return res.data ?? []
}

export async function findFeedstocks(
  query: string,
  double_count_only?: boolean
) {
  const res = await apiFetch.GET("/resources/feedstocks", {
    params: { query: { query, double_count_only } },
  })

  return res.data ?? []
}

export async function findBiofuels(query: string) {
  const res = await apiFetch.GET("/resources/biofuels", {
    params: { query: { query } },
  })

  return res.data ?? []
}

export async function findCountries(
  query: string,
  options?: { exclude_france?: boolean }
) {
  const res = await apiFetch.GET("/resources/countries", {
    params: { query: { query, ...options } },
  })

  let data = res.data ?? []

  if (options?.exclude_france) {
    data = data.filter((country) => country.code_pays !== "FR") ?? []
  }

  return data
}

export async function findEntities(
  query?: string,
  filters?: {
    is_enabled?: boolean
    entity_type?: EntityType[]
    is_tiruert_liable?: boolean
    allowed_tiruert?: boolean
  }
) {
  const res = await apiFetch.GET("/resources/entities", {
    params: { query: { query, ...filters } },
  })

  return res.data ?? []
}

export function findEnabledEntities(query?: string) {
  return findEntities(query, { is_enabled: true })
}

export function findBiofuelEntities(query?: string) {
  return findEntities(query, {
    is_enabled: true,
    entity_type: [
      EntityType.Producer,
      EntityType.Trader,
      EntityType.Operator,
      EntityType.PowerOrHeatProducer,
    ],
  })
}

export function findOperators(query?: string) {
  return findEntities(query, {
    is_enabled: true,
    entity_type: [EntityType.Operator],
  })
}

export function findProducers(query?: string) {
  return findEntities(query, {
    is_enabled: true,
    entity_type: [EntityType.Producer],
  })
}

export async function findProductionSites(
  query?: string,
  producer_id?: number
) {
  const res = await apiFetch.GET("/resources/production-sites", {
    params: { query: { query, producer_id } },
  })

  return res.data ?? []
}

/**
 * Get the delivery sites of an entity
 * @param entity_id - The ID of the entity
 * @returns The delivery sites of the entity
 */
export function getDeliverySites(entity_id: number) {
  return apiFetch.GET("/entities/depots/", {
    params: { query: { entity_id } },
  })
}

export async function findDepots(query?: string, public_only?: boolean) {
  const res = await apiFetch.GET("/resources/depots", {
    params: { query: { query, public_only } },
  })

  return res.data ?? []
}

export async function findAirports(query?: string, public_only?: boolean) {
  const res = await apiFetch.GET("/resources/airports", {
    params: { query: { query, public_only } },
  })

  return res.data ?? []
}

export async function findCertificates(
  query: string,
  options?: { date?: string }
) {
  const res = await apiFetch.GET("/resources/certificates", {
    params: { query: { query, ...options } },
  })

  return res.data?.map((c) => c.certificate_id) ?? []
}

export async function findMyCertificates(
  query: string,
  options: {
    entity_id: number
    production_site_id?: number
    date?: string
  }
) {
  const res = await apiFetch.GET("/entities/certificates/", {
    params: { query: { query, ...options } },
  })
  return (
    res.data?.map(
      (c: { certificate: { certificate_id: string } }) =>
        c.certificate.certificate_id
    ) ?? []
  )
}

export const searchCompanyData = (registration_id: string) => {
  return apiFetch.POST("/entities/search-company/", {
    body: {
      registration_id,
    },
  })
}

export async function findSystemNationalCertificates(query: string) {
  const res = await apiFetch.GET("/resources/systeme-national", {
    params: { query: { query } },
  })
}

export async function findDcAgreements(query: string) {
  const res = await apiFetch.GET("/resources/dc-agreements", {
    params: { query: { query } },
  })
  return res.data ?? []
}
