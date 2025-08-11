import {
  TariffReferenceEnum as TariffReference,
  InstallationCategoryEnum as InstallationCategory,
} from "api-schema"
import { apiTypes } from "common/services/api-fetch.types"

export { TariffReference, InstallationCategory }

// Contracts
export type BiomethaneEntityConfigContract =
  apiTypes["BiomethaneEntityConfigContract"]
export type BiomethaneContractAddRequest =
  apiTypes["BiomethaneEntityConfigContractAddRequest"]
export type BiomethaneContractPatchRequest =
  apiTypes["PatchedBiomethaneEntityConfigContractPatchRequest"]

// Amendments
export type BiomethaneEntityConfigAmendment =
  apiTypes["BiomethaneEntityConfigAmendment"]
export type BiomethaneAmendmentAddRequest =
  apiTypes["BiomethaneEntityConfigAmendmentAddRequest"]
