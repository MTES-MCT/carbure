import { Api } from "common/services/api"
import { api as apiFetch } from "common/services/api-fetch"
import { GESOption, ProductionSiteDetails } from "carbure/types"

export function getProductionSites(entity_id: number) {
  console.log("VERYUNSURE 1")
  return apiFetch.GET("/entities/production-sites/", {
    params: { entity_id },
  })
}

export function addProductionSite(
  entity_id: number,
  name: string,
  date_mise_en_service: string,
  country_code: string,
  ges_option: GESOption,
  site_id: string,
  address: string,
  city: string,
  postal_code: string,
  eligible_dc: boolean,
  dc_reference: string,
  manager_name: string,
  manager_phone: string,
  manager_email: string
) {
  console.log("VERYUNSURE 2")
  return apiFetch.POST("/entities/production-sites/add/", {
    params: { query: entity_id },
    body: {
      name: name,
      date_mise_en_service: date_mise_en_service,
      ges_option: ges_option,
      country_code: country_code,
      site_id,
      address,
      city,
      postal_code,
      eligible_dc,
      dc_reference,
      manager_name,
      manager_phone,
      manager_email,
    },
  })
}

export function updateProductionSite(
  entity_id: number,
  production_site_id: number,
  name: string,
  date_mise_en_service: string,
  country_code: string,
  ges_option: GESOption,
  site_id: string,
  address: string,
  city: string,
  postal_code: string,
  eligible_dc: boolean,
  dc_reference: string,
  manager_name: string,
  manager_phone: string,
  manager_email: string
) {
  console.log("VERYUNSURE 3")
  return apiFetch.POST("/entities/production-sites/{id}/update/", {
    params: { query: entity_id, path: {id: production_site_id} },
    body: {
      name,
      date_mise_en_service,
      ges_option,
      country_code,
      site_id,
      address,
      city,
      postal_code,
      eligible_dc,
      dc_reference,
      manager_name,
      manager_phone,
      manager_email,
    },
  })
}

export function deleteProductionSite(
  entity_id: number | undefined,
  production_site_id: number
) {
  console.log("VERYUNSURE 4")
  return apiFetch.POST("/entities/production-sites/{id}/delete/", {
    params: { query: { entity_id }, path: {id: production_site_id} },
  })
}

export function setProductionSiteFeedstock(
  entity_id: number,
  production_site_id: number,
  matiere_premiere_codes: string[]
) {
  console.log("VERYUNSURE 5")
  return apiFetch.POST("/entities/production-sites/{id}/set-feedstocks/", {
    params: { query: { entity_id }, path: {id: production_site_id} },
    body: { matiere_premiere_codes },
  })
}

export function setProductionSiteBiofuel(
  entity_id: number,
  production_site_id: number,
  biocarburant_codes: string[]
) {
  console.log("VERYUNSURE 6")
  return apiFetch.POST("/entities/production-sites/{id}/set-biofuels/", {
    params: { query: { entity_id }, path: {id: production_site_id} },
    body: { biocarburant_codes },
  })
}

export function setProductionSiteCertificates(
  entity_id: number,
  production_site_id: number,
  certificate_ids: string[]
) {
  console.log("VERYUNSURE 7")
  return apiFetch.POST("/entities/production-sites/{id}/set-certificates/", {
    params: { query: { entity_id }, path: {id: production_site_id} },
    body: { certificate_ids },
  })
}
