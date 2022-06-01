import { AxiosResponse } from "axios"
import { Entity } from "carbure/types"
import {
  Biofuel,
  Feedstock,
  Country,
  Depot,
  Certificate,
  ProductionSiteDetails,
  EntityCertificate,
} from "common/types"

import api, { Api } from "./services/api"

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

export function findProductionSites(query?: string, producer_id?: number) {
  return api
    .get<Api<ProductionSiteDetails[]>>("/v3/common/production-sites", {
      params: { query, producer_id },
    })
    .then(extract)
}

export function findDepots(query: string, entity_id?: number) {
  return api
    .get<Api<Depot[]>>("/v3/common/delivery-sites", {
      params: { query, entity_id },
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
