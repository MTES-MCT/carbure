import api, { ApiResponse } from "./api"

export type Entity = {
  entity: {
    id: number
    name: string
    entity_type: string
  }
}

export type Settings = {
  rights: Entity[]
}

export function getSettings(): ApiResponse<Settings> {
  return api.get("/settings")
}
