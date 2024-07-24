import api, { Api } from "common/services/api"
import {
  Country,
  DepotType,
  Entity,
  EntityDepot,
  OwnershipType,
} from "carbure/types"

export function getDeliverySites(entity_id: number) {
  return api.get<Api<EntityDepot[]>>("/entity/depots", {
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
  blending_entity: Entity | undefined
) {
  return api.post("/entity/depots/add", {
    entity_id,
    delivery_site_id,
    ownership_type,
    blending_outsourced,
    blending_entity_id: blending_entity?.id,
  })
}

export function createNewDeliverySite(
  entity_id: number,
  name: string,
  city: string,
  country: Country,
  depot_id: string,
  depot_type: DepotType,
  address: string,
  postal_code: string,
  ownership_type: OwnershipType,
  blending_outsourced: boolean,
  blending_entity: Entity | undefined,
  electrical_efficiency?: number,
  thermal_efficiency?: number,
  useful_temperature?: number
) {
  // return api.post("/entity/depots/create", {
  //   entity_id,
  //   ownership_type,
  //   blending_outsourced,
  //   blending_entity_id: blending_entity?.id,
  //   name,
  //   city,
  //   country_id: country.code_pays,
  //   delivery_site_id: depot_id,
  //   delivery_site_type: depot_type,
  //   address,
  //   postal_code,
  //   electrical_efficiency,
  //   thermal_efficiency,
  //   useful_temperature,
  // })
  return Promise.resolve(true)
}

export function deleteDeliverySite(
  entity_id: number,
  delivery_site_id: string
) {
  return api.post("/entity/depots/delete", {
    entity_id,
    delivery_site_id,
  })
}
