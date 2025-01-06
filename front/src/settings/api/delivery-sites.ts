import { Api } from "common/services/api"
import { api as apiFetch } from "common/services/api-fetch"
import {
  Country,
  SiteType,
  EntityDepot,
  OwnershipType,
  EntityPreview,
} from "carbure/types"

export function getDeliverySites(entity_id: number) {
  console.log("VERYUNSURE 21")
  return apiFetch.GET("/entities/depots/", {
    params: { entity_id },
  })
}

/**
 * Link an existing delivery site to an entity
 */
export function addDeliverySite(
  entity_id: number,
  delivery_site_id: string,
  ownership_type: OwnershipType,
  blending_outsourced: boolean,
  blending_entity: EntityPreview | undefined
) {
  console.log("VERYUNSURE 22")
  return apiFetch.POST("/entities/depots/add", {
    params: { query: { entity_id } },
    body: {
      delivery_site_id,
      ownership_type,
      blending_outsourced,
      blending_entity_id: blending_entity?.id,
    },
  })
}

export function createNewDeliverySite(
  entity_id: number,
  name: string,
  city: string,
  country: Country,
  depot_id: string,
  depot_type: SiteType,
  address: string,
  postal_code: string,
  electrical_efficiency?: number,
  thermal_efficiency?: number,
  useful_temperature?: number
) {
  console.log("VERYUNSURE 23")
  return apiFetch.POST("/entities/depots/create", {
    params: { query: { entity_id } },
    body: {
      name,
      city,
      country_code: country.code_pays,
      depot_id,
      depot_type,
      address,
      postal_code,
      electrical_efficiency,
      thermal_efficiency,
      useful_temperature,
    },
  })
}

export function deleteDeliverySite(
  entity_id: number,
  delivery_site_id: string
) {
  console.log("VERYUNSURE 24")
  return apiFetch.POST("/entities/depots/delete", {
    params: { query: { entity_id } },
    body: {
      delivery_site_id,
    },
  })
}
