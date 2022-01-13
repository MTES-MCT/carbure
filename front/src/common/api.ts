import {
  Biocarburant,
  Country,
  DeliverySite,
  Entity,
  MatierePremiere,
  ProductionSiteDetails,
} from "./types"

import api from "./services/api"

export function findMatieresPremieres(
  query: string,
  double_count_only?: boolean
): Promise<MatierePremiere[]> {
  return api.get("/common/matieres-premieres", { query, double_count_only })
}

export function findBiocarburants(query: string): Promise<Biocarburant[]> {
  return api.get("/common/biocarburants", { query })
}

export function findCountries(query: string): Promise<Country[]> {
  return api.get("/common/countries", { query })
}

export function findEntities(query?: string): Promise<Entity[]> {
  return api.get("/common/entities", { query })
}

export function findOperators(query: string): Promise<Entity[]> {
  return api.get("/common/operators", { query })
}

export function findProductionSites(
  query?: string,
  producerID?: number
): Promise<ProductionSiteDetails[]> {
  return api.get("/common/production-sites", { query, producer_id: producerID })
}

export function findDeliverySites(
  query: string,
  entity_id?: number
): Promise<DeliverySite[]> {
  return api.get("/common/delivery-sites", { query, entity_id })
}

export function findCertificates(
  query: string,
  entity_id?: number | null,
  production_site?: number | null
): Promise<string[]> {
  return api.get("/common/certificates", { query, entity_id, production_site })
}
