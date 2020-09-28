import api, { ApiPromise } from "./api"
import { Settings } from "./types"

export function getSettings(): ApiPromise<Settings> {
  return api.get("/settings")
}
