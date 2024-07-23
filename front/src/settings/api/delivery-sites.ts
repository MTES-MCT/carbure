import api, { Api } from "common/services/api"
import { Entity, EntityDepot, OwnershipType } from "carbure/types"

export function getDeliverySites(entity_id: number) {
	return api.get<Api<EntityDepot[]>>("/entity/depots", {
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
	return api.post("/entity/depots/add", {
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
	return api.post("/entity/depots/delete", {
		entity_id,
		delivery_site_id,
	})
}
