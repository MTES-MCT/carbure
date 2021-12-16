import api, { Api } from "common-v2/services/api"
import { User } from "./types"

export function getUserSettings() {
  return api.get<Api<User>>("v3/settings/")
}
