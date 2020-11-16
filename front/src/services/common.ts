import {
  Biocarburant,
  Country,
  DBSCertificate,
  DeliverySite,
  Entity,
  ISCCCertificate,
  MatierePremiere,
  ProductionSiteDetails,
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
): Promise<ProductionSiteDetails[]> {
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

export function findISCCCertificates(
  query: string
): Promise<ISCCCertificate[]> {
  return api.get("/common/iscc-certificates", {
    query: query,
  })
}

export function find2BSCertificates(query: string): Promise<DBSCertificate[]> {
  return api.get("/common/2bs-certificates", {
    query: query,
  })
}

export function addDeliverySite(
  name: string,
  city: string,
  country: string,
  depotID: string,
  depotType: string
): Promise<any> {
  return api.post("/common/create-delivery-site", {
    name: name,
    city: city,
    country_code: country,
    depot_id: depotID,
    depot_type: depotType,
  })
}
