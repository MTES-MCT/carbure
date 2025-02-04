import { api as apiFetch } from "common/services/api-fetch"
import { Country, SiteType, OwnershipType, EntityPreview } from "carbure/types"

export function getDeliverySites(entity_id: number) {
  return apiFetch.GET("/entities/depots/", {
    params: { query: { entity_id } },
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
  return apiFetch.POST("/entities/depots/add/", {
    params: { query: { entity_id } },
    body: {
      delivery_site_id,
      ownership_type,
      blending_is_outsourced: blending_outsourced,
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
  return apiFetch.POST("/entities/depots/create-depot/", {
    params: { query: { entity_id } },
    body: {
      entity_id,
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
  return apiFetch.POST("/entities/depots/delete-depot/", {
    params: { query: { entity_id } },
    body: {
      delivery_site_id,
    },
  })
}
