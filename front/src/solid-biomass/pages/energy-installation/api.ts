import { api } from "common/services/api-fetch"
import { map } from "ramda"
import { InstallationRequest } from "./types"

export function getInstallation(entity_id: number) {
  return api.GET("/solid-biomass/energy-installation/", {
    params: { query: { entity_id } },
  })
}

export function saveInstallation(entity_id: number, data: InstallationRequest) {
  return api.PUT("/solid-biomass/energy-installation/", {
    params: { query: { entity_id } },
    body: map((value) => value ?? "", data) as InstallationRequest,
  })
}
