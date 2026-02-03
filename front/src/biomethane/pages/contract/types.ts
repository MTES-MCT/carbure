import {
  InstallationCategoryEnum as InstallationCategory,
  TrackedAmendmentTypesEnum as TrackedAmendmentTypes,
  ComplementaryAidOrganismsEnum as ComplementaryAidOrganisms,
  PathsApiBiomethaneAdminAnnualDeclarationsGetParametersQueryTariff_reference as TariffReference,
} from "api-schema"
import { apiTypes } from "common/services/api-fetch.types"

export {
  TariffReference,
  InstallationCategory,
  TrackedAmendmentTypes,
  ComplementaryAidOrganisms,
}

// Contracts
export type BiomethaneContract = apiTypes["BiomethaneContract"]
export type BiomethaneContractPatchRequest =
  apiTypes["BiomethaneContractInputRequest"]

// Amendments
export type BiomethaneContractAmendment =
  apiTypes["BiomethaneContractAmendment"]
export type BiomethaneAmendmentAddRequest =
  apiTypes["BiomethaneContractAmendmentAddRequest"]
