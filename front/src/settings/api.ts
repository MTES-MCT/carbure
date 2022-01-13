import api from "common/services/api"
import {
  GESOption,
  ProductionSite,
  ProductionSiteDetails,
  OwnershipType,
  EntityRights,
} from "common/types"
import {
  DoubleCounting,
  DoubleCountingDetails,
  QuotaDetails,
} from "doublecount/types"
import { Entity } from "carbure/types"
import { EntityDeliverySite } from "./hooks/use-delivery-sites"

export function getProductionSites(
  entityID: number
): Promise<ProductionSiteDetails[]> {
  return api.get("/settings/get-production-sites", {
    entity_id: entityID,
  })
}

export function addProductionSite(
  producerID: number,
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
): Promise<ProductionSite> {
  return api.post("/settings/add-production-site", {
    entity_id: producerID,
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
  city: string,
  postal_code: string,
  eligible_dc: boolean,
  dc_reference: string,
  manager_name: string,
  manager_phone: string,
  manager_email: string
) {
  return api.post("/settings/update-production-site", {
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
  productionSiteID: number
) {
  return api.post("/settings/delete-production-site", {
    entity_id: entity_id,
    production_site_id: productionSiteID,
  })
}

export function setProductionSiteMP(
  entity_id: number,
  productionSiteID: number,
  matieresPremieres: string[]
) {
  return api.post("/settings/set-production-site-matieres-premieres", {
    entity_id: entity_id,
    production_site_id: productionSiteID,
    matiere_premiere_codes: matieresPremieres,
  })
}

export function setProductionSiteBC(
  entity_id: number,
  productionSiteID: number,
  biocarburants: string[]
) {
  return api.post("/settings/set-production-site-biocarburants", {
    entity_id: entity_id,
    production_site_id: productionSiteID,
    biocarburant_codes: biocarburants,
  })
}

export function getDeliverySites(entity_id: number) {
  return api.get<EntityDeliverySite[]>("/settings/get-delivery-sites", {
    entity_id,
  })
}

export function addDeliverySite(
  entity_id: number,
  delivery_site_id: string,
  ownership_type: OwnershipType,
  blending_outsourced: boolean,
  blending_entity: Entity | null
) {
  return api.post("/settings/add-delivery-site", {
    entity_id,
    delivery_site_id,
    ownership_type,
    blending_outsourced,
    blending_entity_id: blending_entity?.id ?? null,
  })
}

export function deleteDeliverySite(
  entity_id: number,
  delivery_site_id: string
) {
  return api.post("/settings/delete-delivery-site", {
    entity_id,
    delivery_site_id,
  })
}

export function enableMAC(entityID: number) {
  return api.post("/settings/enable-mac", {
    entity_id: entityID,
  })
}

export function disableMAC(entityID: number) {
  return api.post("/settings/disable-mac", {
    entity_id: entityID,
  })
}

export function enableTrading(entityID: number) {
  return api.post("/settings/enable-trading", {
    entity_id: entityID,
  })
}

export function disableTrading(entityID: number) {
  return api.post("/settings/disable-trading", {
    entity_id: entityID,
  })
}

export function getEntityRights(entity_id: number): Promise<EntityRights> {
  return api.get("/settings/get-entity-rights", { entity_id })
}

export function revokeUserRights(entity_id: number, email: string) {
  return api.post("/settings/revoke-user", { entity_id, email })
}

export function acceptUserRightsRequest(entity_id: number, request_id: number) {
  return api.post("/settings/accept-user", { entity_id, request_id })
}

export function getDoubleCountingAgreements(entity_id: number) {
  return api.get<DoubleCounting[]>("/doublecount/agreements", { entity_id })
}

export function getDoubleCountingDetails(entity_id: number, dca_id: number) {
  return api.get<DoubleCountingDetails>("/doublecount/agreement", {
    entity_id,
    dca_id,
  })
}

export function uploadDoubleCountingFile(
  entity_id: number,
  production_site_id: number,
  file: File
) {
  return api.post<{ dca_id: number }>("/doublecount/upload", {
    entity_id,
    production_site_id,
    file,
  })
}

export function uploadDoubleCountingDescriptionFile(
  entity_id: number,
  dca_id: number,
  file: File
) {
  return api.post("/doublecount/upload-documentation", {
    entity_id,
    dca_id,
    file,
  })
}

export function addDoubleCountingSourcing(
  entity_id: number,
  dca_id: number,
  year: number,
  metric_tonnes: number,
  feedstock_code: string,
  origin_country_code: string,
  supply_country_code: string,
  transit_country_code: string
) {
  return api.post("/doublecount/agreement/add-sourcing", {
    entity_id,
    dca_id,
    year,
    metric_tonnes,
    feedstock_code,
    origin_country_code,
    supply_country_code,
    transit_country_code,
  })
}

export function updateDoubleCountingSourcing(
  entity_id: number,
  dca_sourcing_id: number,
  metric_tonnes: number
) {
  return api.post("/doublecount/agreement/update-sourcing", {
    entity_id,
    dca_sourcing_id,
    metric_tonnes,
  })
}

export function deleteDoubleCountingSourcing(
  entity_id: number,
  dca_sourcing_id: number
) {
  return api.post("/doublecount/agreement/remove-sourcing", {
    entity_id,
    dca_sourcing_id,
  })
}

export function addDoubleCountingProduction(
  entity_id: number,
  dca_id: number,
  year: number,
  feedstock_code: string,
  biofuel_code: string,
  estimated_production: number,
  max_production_capacity: number,
  requested_quota: number
) {
  return api.post("/doublecount/agreement/add-production", {
    entity_id,
    dca_id,
    year,
    feedstock_code,
    biofuel_code,
    estimated_production,
    max_production_capacity,
    requested_quota,
  })
}

export function updateDoubleCountingProduction(
  entity_id: number,
  dca_production_id: number,
  estimated_production: number,
  max_production_capacity: number,
  requested_quota: number
) {
  return api.post("/doublecount/agreement/update-production", {
    entity_id,
    dca_production_id,
    estimated_production,
    max_production_capacity,
    requested_quota,
  })
}

export function deleteDoubleCountingProduction(
  entity_id: number,
  dca_production_id: number
) {
  return api.post("/doublecount/agreement/remove-production", {
    entity_id,
    dca_production_id,
  })
}

export function getQuotaDetails(entity_id: number, dca_id: number) {
  return api.get<QuotaDetails[]>("/doublecount/quotas", { entity_id, dca_id })
}
