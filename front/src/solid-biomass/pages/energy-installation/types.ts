import { apiTypes } from "common/services/api-fetch.types"

export type Installation = apiTypes["EnergyInstallation"]
export type InstallationRequest = apiTypes["EnergyInstallationRequest"]

export type InstallationCardProps = {
  installation: Installation
  readOnly: boolean
  save: (data: InstallationRequest) => Promise<unknown>
  loading: boolean
}
