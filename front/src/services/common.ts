import { Option } from "../components/system/select"

import api from "./api"

function toOption(valueKey: string, labelKey: string): (v: any) => Option[] {
  return (data: any[]) =>
    data.map((item) => ({
      value: item[valueKey],
      label: item[labelKey],
    }))
}

export function findMatieresPremieres(query: string): Promise<Option[]> {
  return api
    .get("/common/matieres-premieres", { query })
    .then(toOption("code", "name"))
}

export function findBiocarburants(query: string): Promise<Option[]> {
  return api
    .get("/common/biocarburants", { query })
    .then(toOption("code", "name"))
}

export function findCountries(query: string): Promise<Option[]> {
  return api
    .get("/common/countries", { query })
    .then(toOption("code_pays", "name"))
}

export function findEntities(query: string): Promise<Option[]> {
  return api.get("/common/entities", { query }).then(toOption("id", "name"))
}

export function findProducers(query: string): Promise<Option[]> {
  return api.get("/common/producers", { query }).then(toOption("id", "name"))
}

export function findOperators(query: string): Promise<Option[]> {
  return api.get("/common/operators", { query }).then(toOption("id", "name"))
}

export function findTraders(query: string): Promise<Option[]> {
  return api.get("/common/traders", { query }).then(toOption("id", "name"))
}

export function findDeliverySites(query: string): Promise<Option[]> {
  return api
    .get("/common/delivery-sites", { query })
    .then(toOption("depot_id", "name"))
}

export function findProductionSites(query: string): Promise<Option[]> {
  return api
    .get("/common/production-sites", { query })
    .then(toOption("id", "name"))
}

export function findGHG(
  biocarburant_code: string,
  matiere_premiere_code: string
): Promise<Option[]> {
  return api.get("/common/ghg", { biocarburant_code, matiere_premiere_code })
}
