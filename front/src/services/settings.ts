import api from "./api"
import { Settings, GESOption } from "./types"

export function getSettings(): Promise<Settings> {
  return api.get("/settings/")
}

export function addProductionSite(
  entityID: number,
  name: string,
  date_mise_en_service: string,
  ges_option: boolean,
  country_code: string
) {
  return api.post("/settings/add-production-site", {
    entity_id: entityID,
    name: name,
    date_mise_en_service: date_mise_en_service,
    ges_option: ges_option ? GESOption.Actual : GESOption.Default,
    country_code: country_code,
  })
}

export function addProductionSiteMP(
  productionSiteID: number,
  matiere_premiere_code: string
) {
  return api.post("/settings/add-production-site-matiere-premiere", {
    production_site_id: productionSiteID,
    matiere_premiere_code: matiere_premiere_code,
  })
}

export function addProductionSiteBC(
  productionSiteID: number,
  biocarburant_code: string
) {
  return api.post("/settings/add-production-site-biocarburant", {
    production_site_id: productionSiteID,
    biocarburant_code: biocarburant_code,
  })
}

export function deleteProductionSite(productionSiteID: number) {
  return api.post("/settings/delete-production-site", {
    production_site_id: productionSiteID,
  })
}

export function deleteProductionSiteMP(
  productionSiteID: number,
  matiere_premiere_code: string
) {
  return api.post("/settings/delete-production-site-matiere-premiere", {
    production_site_id: productionSiteID,
    matiere_premiere_code: matiere_premiere_code,
  })
}

export function deleteProductionSiteBC(
  productionSiteID: number,
  biocarburant_code: string
) {
  return api.post("/settings/delete-production-site-biocarburant", {
    production_site_id: productionSiteID,
    biocarburant_code: biocarburant_code,
  })
}

export function enablePublicDirectory(entityID: number) {
  return api.post("/settings/enable-public-directory", {
    entity_id: entityID,
  })
}

export function disablePublicDirectory(entityID: number) {
  return api.post("/settings/disable-public-directory", {
    entity_id: entityID,
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

export function getISCCTradingCertificates(entityID: number) {
  return api.get("/settings/get-iscc-trading-certificates", {
    entity_id: entityID,
  })
}

export function addISCCTradingCertificate(
  entityID: number,
  certificate_id: string
) {
  return api.post("/settings/add-iscc-trading-certificate", {
    entity_id: entityID,
    certificate_id: certificate_id,
  })
}

export function deleteISCCTradingCertificate(
  productionSiteID: number,
  certificate_id: string
) {
  return api.post("/settings/delete-iscc-trading-certificate", {
    production_site_id: productionSiteID,
    certificate_id: certificate_id,
  })
}

export function get2BSTradingCertificates(entityID: number) {
  return api.get("/settings/get-2bs-trading-certificates", {
    entity_id: entityID,
  })
}

export function add2BSTradingCertificate(
  entityID: number,
  certificate_id: string
) {
  return api.post("/settings/add-2bs-trading-certificate", {
    entity_id: entityID,
    certificate_id: certificate_id,
  })
}

export function delete2BSTradingCertificate(
  productionSiteID: number,
  certificate_id: string
) {
  return api.post("/settings/delete-2bs-trading-certificate", {
    production_site_id: productionSiteID,
    certificate_id: certificate_id,
  })
}
