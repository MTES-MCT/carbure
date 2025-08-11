import {
  TariffReferenceEnum as TariffReference,
  InstallationCategoryEnum as InstallationCategory,
} from "api-schema"
import { apiTypes } from "common/services/api-fetch.types"

export { TariffReference, InstallationCategory }

// Contracts
export type BiomethaneContract = apiTypes["BiomethaneContract"]
export type BiomethaneContractAddRequest =
  apiTypes["BiomethaneContractAddRequest"]
export type BiomethaneContractPatchRequest =
  apiTypes["PatchedBiomethaneContractPatchRequest"]

// Amendments
export type BiomethaneContractAmendment =
  apiTypes["BiomethaneContractAmendment"]
export type BiomethaneAmendmentAddRequest =
  apiTypes["BiomethaneContractAmendmentAddRequest"]
