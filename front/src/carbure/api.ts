import api, { Api } from "common/services/api"
import { AxiosResponse } from "axios"
import {
  User,
  Notification,
  Entity,
  Biofuel,
  Feedstock,
  Country,
  Depot,
  Certificate,
  ProductionSiteDetails,
  EntityCertificate,
} from "./types"

export function getUserSettings() {
  return api.get<Api<User>>("/v5/user")
}

export function extract<T>(res: AxiosResponse<Api<T[]>>) {
  return res.data.data ?? []
}

export function findFeedstocks(query: string, double_count_only?: boolean) {
  return api
    .get<Api<Feedstock[]>>("/v3/common/matieres-premieres", {
      params: { query, double_count_only },
    })
    .then(extract)
}

export function findBiofuels(query: string) {
  return api
    .get<Api<Biofuel[]>>("/v3/common/biocarburants", { params: { query } })
    .then(extract)
}

export function findCountries(query: string) {
  return api
    .get<Api<Country[]>>("/v3/common/countries", { params: { query } })
    .then(extract)
}

export function findEntities(query?: string) {
  return api
    .get<Api<Entity[]>>("/v3/common/entities", { params: { query } })
    .then(extract)
}

export function findOperators(query?: string) {
  return api
    .get<Api<Entity[]>>("/v3/common/operators", { params: { query } })
    .then(extract)
}

export function findProducers(query?: string) {
  return api
    .get<Api<Entity[]>>("/v3/common/producers", { params: { query } })
    .then(extract)
}

export function findProductionSites(query?: string, producer_id?: number) {
  return api
    .get<Api<ProductionSiteDetails[]>>("/v3/common/production-sites", {
      params: { query, producer_id },
    })
    .then(extract)
}

export function findDepots(query?: string, public_only?: boolean) {
  return api
    .get<Api<Depot[]>>("/v3/common/delivery-sites", {
      params: { query, public_only },
    })
    .then(extract)
}

export function findCertificates(query: string) {
  return api
    .get<Api<Certificate[]>>("/get-certificates", { params: { query } })
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
    .get<Api<EntityCertificate[]>>("/get-my-certificates", {
      params: { query, ...options },
    })
    .then(extract)
    .then((certificates) =>
      certificates.map((c) => c.certificate.certificate_id)
    )
}

export async function getNotifications(entity_id: number) {
  if (entity_id === -1) return
  return api.get<Api<Notification[]>>("/v5/notifications", {
    params: { entity_id },
  })
}

export function ackNotifications(
  entity_id: number,
  notification_ids: number[]
) {
  return api.post("/v5/notifications/ack", {
    entity_id,
    notification_ids,
  })
}
