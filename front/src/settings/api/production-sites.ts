import { api as apiFetch } from "common/services/api-fetch"
import { GESOption } from "common/types"

export function getProductionSites(entity_id: number) {
  return apiFetch.GET("/entities/production-sites/", {
    params: { query: { entity_id } },
  })
}

export function addProductionSite(
  entity_id: number,
  name: string,
  date_mise_en_service: string,
  country_code: string,
  ges_option: GESOption,
  site_siret: string,
  address: string,
  city: string,
  postal_code: string,
  eligible_dc: boolean,
  dc_reference: string,
  manager_name: string,
  manager_phone: string,
  manager_email: string,
  inputs: string[],
  outputs: string[],
  certificates: string[]
) {
  return apiFetch.POST("/entities/production-sites/", {
    params: { query: { entity_id } },
    body: {
      name: name,
      date_mise_en_service: date_mise_en_service,
      ges_option: ges_option,
      country_code: country_code,
      site_siret,
      address,
      city,
      postal_code,
      eligible_dc,
      dc_reference,
      manager_name,
      manager_phone,
      manager_email,
      inputs,
      outputs,
      certificates,
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
  site_siret: string,
  address: string,
  city: string,
  postal_code: string,
  eligible_dc: boolean,
  dc_reference: string,
  manager_name: string,
  manager_phone: string,
  manager_email: string,
  inputs: string[],
  outputs: string[],
  certificates: string[]
) {
  return apiFetch.PUT("/entities/production-sites/{id}/", {
    params: { query: { entity_id }, path: { id: production_site_id } },
    body: {
      name,
      date_mise_en_service,
      ges_option,
      country_code,
      site_siret,
      address,
      city,
      postal_code,
      eligible_dc,
      dc_reference,
      manager_name,
      manager_phone,
      manager_email,
      inputs,
      outputs,
      certificates,
    },
  })
}

export function deleteProductionSite(
  entity_id: number,
  production_site_id: number
) {
  return apiFetch.DELETE("/entities/production-sites/{id}/", {
    params: { query: { entity_id }, path: { id: production_site_id } },
  })
}
