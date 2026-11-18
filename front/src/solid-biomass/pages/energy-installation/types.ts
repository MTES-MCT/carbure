import { components } from "api-schema"

export type Installation = components["schemas"]["EnergyInstallation"]
export type InstallationRequest =
  components["schemas"]["EnergyInstallationRequest"]

export type InstallationCardProps = {
  installation: Installation
  readOnly: boolean
  save: (data: InstallationRequest) => Promise<unknown>
  loading: boolean
}
