import api from "common/services/api"
import { Entity } from "carbure/types"
import {
  ProductionSite,
  OwnershipType,
  GESOption,
  ProductionSiteDetails,
} from "common/types"
import {
  DoubleCounting,
  DoubleCountingDetails,
  QuotaDetails,
} from "doublecount/types"
import { EntityRights } from "./types"
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
