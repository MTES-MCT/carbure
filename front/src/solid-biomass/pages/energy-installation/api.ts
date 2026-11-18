import { api } from "common/services/api-fetch"
import { InstallationRequest } from "./types"

export const getInstallation = async (entity_id: number) =>
  (
    await api.GET("/solid-biomass/energy-installation/", {
      params: { query: { entity_id } },
    })
  ).data

export const saveInstallation = async (
  entity_id: number,
  data: InstallationRequest
) =>
  (
    await api.PUT("/solid-biomass/energy-installation/", {
      params: { query: { entity_id } },
      body: Object.fromEntries(
        Object.entries(data).map(([key, value]) => [key, value ?? ""])
      ) as InstallationRequest,
    })
  ).data
