import api, { ApiResponse } from "./api"

export type Entity = {
  id: number
  name: string
  entity_type: string
}

export type Settings = {
  email: string
  rights: { entity: Entity }[]
}

export function getSettings(): ApiResponse<Settings> {
  return api.get("/settings")
}
