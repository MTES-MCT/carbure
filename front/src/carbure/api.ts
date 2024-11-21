import api, { Api } from "common/services/api"
import { AxiosResponse } from "axios"
import { api as apiFetch } from "common/services/api-fetch"
import {
  User,
  Notification,
  Entity,
  Biofuel,
  Country,
  Certificate,
  EntityType,
  ProductionSiteDetails,
  EntityCertificate,
} from "./types"

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

export function findBiofuels(query: string) {
  return api
    .get<Api<Biofuel[]>>("/resources/biofuels", { params: { query } })
    .then(extract)
}

export function findCountries(query: string) {
  return api
    .get<Api<Country[]>>("/resources/countries", { params: { query } })
    .then(extract)
}

export function findEntities(
  query?: string,
  filters?: { is_enabled?: boolean; entity_type?: EntityType[] }
) {
  return api
    .get<
      Api<Entity[]>
    >("/resources/entities", { params: { query, ...filters } })
    .then(extract)
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
  return api
    .get<Api<Entity[]>>("/resources/operators", { params: { query } })
    .then(extract)
}

export function findProducers(query?: string) {
  return api
    .get<Api<Entity[]>>("/resources/producers", { params: { query } })
    .then(extract)
}

export function findProductionSites(query?: string, producer_id?: number) {
  return api
    .get<Api<ProductionSiteDetails[]>>("/resources/production-sites", {
      params: { query, producer_id },
    })
    .then(extract)
}

export async function findDepots(query?: string, public_only?: boolean) {
  const res = await apiFetch.GET("/resources/depots", {
    params: { query: { query, public_only } },
  })

  return res.data ?? []
}

export function findCertificates(query: string) {
  return api
    .get<Api<Certificate[]>>("/resources/certificates", {
      params: { query },
    })
    .then(extract)
    .then((certificates) => certificates.map((c) => c.certificate_id))
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
