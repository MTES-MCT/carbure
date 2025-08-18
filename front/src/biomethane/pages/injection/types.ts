import { NetworkTypeEnum as NetworkType } from "api-schema"
import { apiTypes } from "common/services/api-fetch.types"

export { NetworkType }

// Injection Sites
export type BiomethaneInjectionSite = apiTypes["BiomethaneInjectionSite"]
export type BiomethaneInjectionSiteAddRequest =
  apiTypes["BiomethaneInjectionSiteInputRequest"]
