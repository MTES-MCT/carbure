import {
  Biocarburant,
  Country,
  DeliverySite,
  Entity,
  MatierePremiere,
  ProductionSite,
} from "./types"

import api from "./api"

export function findMatieresPremieres(
  query: string
): Promise<MatierePremiere[]> {
  return api.get("/common/matieres-premieres", { query })
}

export function findBiocarburants(query: string): Promise<Biocarburant[]> {
  return api.get("/common/biocarburants", { query })
}

export function findCountries(query: string): Promise<Country[]> {
  return api.get("/common/countries", { query })
}

export function findEntities(query: string): Promise<Entity[]> {
  return api.get("/common/entities", { query })
}

export function findProducers(query: string): Promise<Entity[]> {
  return api.get("/common/producers", { query })
}

export function findOperators(query: string): Promise<Entity[]> {
  return api.get("/common/operators", { query })
}

export function findTraders(query: string): Promise<Entity[]> {
  return api.get("/common/traders", { query })
}

export function findProductionSites(
  query?: string,
  producerID?: number
): Promise<ProductionSite[]> {
  return api.get("/common/production-sites", { query, producer_id: producerID })
}

export function findDeliverySites(query: string): Promise<DeliverySite[]> {
  return api.get("/common/delivery-sites", { query })
}

export function findGHG(
  biocarburant_code: string,
  matiere_premiere_code: string
): Promise<any[]> {
  return api.get("/common/ghg", { biocarburant_code, matiere_premiere_code })
}

export function findISCCCertificates(query: string) {
  return api.get("/common/iscc-certificates", {
    query: query,
  })
}

export function find2BSCertificates(query: string) {
  return api.get("/common/2bs-certificates", {
    query: query,
  })
}
