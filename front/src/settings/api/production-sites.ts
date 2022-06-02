import api, { Api } from "common/services/api"
import { GESOption, ProductionSiteDetails } from "carbure/types"

export function getProductionSites(entity_id: number) {
  return api.get<Api<ProductionSiteDetails[]>>(
    "/v3/settings/get-production-sites",
    { params: { entity_id } }
  )
}

export function addProductionSite(
  entity_id: number,
  name: string,
  date_mise_en_service: string,
  country_code: string,
  ges_option: GESOption,
  site_id: string,
  city: string,
  postal_code: string,
  eligible_dc: boolean,
  dc_reference: string,
  manager_name: string,
  manager_phone: string,
  manager_email: string
) {
  return api.post<Api<ProductionSiteDetails>>(
    "/v3/settings/add-production-site",
    {
      entity_id,
      name: name,
      date_mise_en_service: date_mise_en_service,
      ges_option: ges_option,
      country_code: country_code,
      site_id,
      city,
      postal_code,
      eligible_dc,
      dc_reference,
      manager_name,
      manager_phone,
      manager_email,
    }
  )
}

export function updateProductionSite(
  entity_id: number,
  production_site_id: number,
  name: string,
  date_mise_en_service: string,
  country_code: string,
  ges_option: GESOption,
  site_id: string,
  city: string,
  postal_code: string,
  eligible_dc: boolean,
  dc_reference: string,
  manager_name: string,
  manager_phone: string,
  manager_email: string
) {
  return api.post("/v3/settings/update-production-site", {
    entity_id,
    production_site_id,
    name,
    date_mise_en_service,
    ges_option,
    country_code,
    site_id,
    city,
    postal_code,
    eligible_dc,
    dc_reference,
    manager_name,
    manager_phone,
    manager_email,
  })
}

export function deleteProductionSite(
  entity_id: number | undefined,
  production_site_id: number
) {
  return api.post("/v3/settings/delete-production-site", {
    entity_id,
    production_site_id,
  })
}

export function setProductionSiteFeedstock(
  entity_id: number,
  production_site_id: number,
  matiere_premiere_codes: string[]
) {
  return api.post("/v3/settings/set-production-site-matieres-premieres", {
    entity_id,
    production_site_id,
    matiere_premiere_codes,
  })
}

export function setProductionSiteBiofuel(
  entity_id: number,
  production_site_id: number,
  biocarburant_codes: string[]
) {
  return api.post("/v3/settings/set-production-site-biocarburants", {
    entity_id: entity_id,
    production_site_id,
    biocarburant_codes,
  })
}

export function setProductionSiteCertificates(
  entity_id: number,
  production_site_id: number,
  certificate_ids: string[]
) {
  return api.post("/set-production-site-certificates", {
    entity_id,
    production_site_id,
    certificate_ids,
  })
}
