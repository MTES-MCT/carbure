import api, { ApiResponse } from "./api"


export type Snapshot = {
  lots: {
    drafts: number
    validated: number
    tofix: number
    accepted: number
  }

  filters: {
    [k: string]: any[]
  }
}


export function getSnapshot(producerID: number): ApiResponse<Snapshot> {
  return api.get("/lots/snapshot", { producer_id: producerID })
}
