import api, { Api } from "common/services/api"
import { AxiosResponse } from "axios"
import { api as apiFetch } from "common/services/api-fetch"
import { User, Notification, EntityType, EntityCertificate } from "./types"

export function getUserSettings() {
  return api.get<Api<User>>("/user")
}

export function extract<T>(res: AxiosResponse<Api<T[]>>) {
  return res.data.data ?? []
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

export async function findCountries(query: string) {
  const res = await apiFetch.GET("/resources/countries", {
    params: { query: { query } },
  })

  return res.data ?? []
}

export async function findEntities(
  query?: string,
  filters?: { is_enabled?: boolean; entity_type?: EntityType[] }
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

export async function findDepots(query?: string, public_only?: boolean) {
  const res = await apiFetch.GET("/resources/depots", {
    params: { query: { query, public_only } },
  })

  return res.data ?? []
}

export async function findCertificates(query: string) {
  const res = await apiFetch.GET("/resources/certificates", {
    params: { query: { query } },
  })

  return res.data?.map((c) => c.certificate_id) ?? []
}

export function findMyCertificates(
  query: string,
  options: {
    entity_id?: number | null
    production_site_id?: number | null | undefined
  }
) {
  return api
    .get<Api<EntityCertificate[]>>("/entity/certificates", {
      params: { query, ...options },
    })
    .then(extract)
    .then((certificates) =>
      certificates.map((c) => c.certificate.certificate_id)
    )
}

export async function getNotifications(entity_id: number) {
  if (entity_id === -1) return
  return api.get<Api<Notification[]>>("/entity/notifications", {
    params: { entity_id },
  })
}

export function ackNotifications(
  entity_id: number,
  notification_ids: number[]
) {
  return api.post("/entity/notifications/ack", {
    entity_id,
    notification_ids,
  })
}
