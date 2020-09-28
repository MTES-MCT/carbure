import api from "./api"
import { Settings } from "./types"

export function getSettings(): Promise<Settings> {
  return api.get("/settings")
}
