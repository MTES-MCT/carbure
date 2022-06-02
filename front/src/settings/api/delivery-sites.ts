import { Entity } from "carbure/types"
import api, { Api } from "common/services/api"
import { EntityDepot, OwnershipType } from "common/types"

export function getDeliverySites(entity_id: number) {
  return api.get<Api<EntityDepot[]>>("/v3/settings/get-delivery-sites", {
    params: { entity_id },
  })
}

export function addDeliverySite(
  entity_id: number,
  delivery_site_id: string,
  ownership_type: OwnershipType,
  blending_outsourced: boolean,
  blending_entity: Entity | undefined
) {
  return api.post("/v3/settings/add-delivery-site", {
    entity_id,
    delivery_site_id,
    ownership_type,
    blending_outsourced,
    blending_entity_id: blending_entity?.id,
  })
}

export function deleteDeliverySite(
  entity_id: number,
  delivery_site_id: string
) {
  return api.post("/v3/settings/delete-delivery-site", {
    entity_id,
    delivery_site_id,
  })
}
