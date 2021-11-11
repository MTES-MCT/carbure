import { AxiosResponse } from "axios"
import {
  Biofuel,
  Feedstock,
  Country,
  DeliverySite,
  Entity,
  ProductionSiteDetails,
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

export function findProductionSites(query?: string, producer_id?: number) {
  return api
    .get<Api<ProductionSiteDetails[]>>("/v3/common/production-sites", {
      params: { query, producer_id },
    })
    .then(extract)
}

export function findDepots(query: string, entity_id?: number) {
  return api
    .get<Api<DeliverySite[]>>("/v3/common/delivery-sites", {
      params: { query, entity_id },
    })
    .then(extract)
}

export function findCertificates(
  query: string,
  options: {
    entity_id?: number | null
    production_site?: number | null | undefined
  }
) {
  return api
    .get<Api<string[]>>("/v3/common/certificates", {
      params: { query, ...options },
    })
    .then(extract)
}
