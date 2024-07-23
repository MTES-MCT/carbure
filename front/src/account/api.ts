import api from "common/services/api"
import { UserRole } from "carbure/types"

export function requestAccess(entity_id: number, role: UserRole, comment = "") {
	return api.post("/user/request-access", {
		entity_id,
		comment,
		role,
	})
}

export function revokeMyself(entity_id: number) {
	return api.post("/user/revoke-access", { entity_id })
}
