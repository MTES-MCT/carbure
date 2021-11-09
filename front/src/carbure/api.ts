import api, { Api } from "common-v2/api"
import { UserSettings } from "./types"

export function getUserSettings() {
  return api.get<Api<UserSettings>>("v3/settings")
}
