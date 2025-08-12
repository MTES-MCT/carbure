import {
  TariffReferenceEnum as TariffReference,
  InstallationCategoryEnum as InstallationCategory,
  UnitTypeEnum as UnitType,
  HygienizationExemptionTypeEnum as HygienizationExemptionType,
  IcpeRegimeEnum as IcpeRegime,
  ProcessTypeEnum as ProcessType,
  MethanizationProcessEnum as MethanizationProcess,
  DigestateValorizationMethodEnum as DigestateValorizationMethod,
  SpreadingManagementEnum as SpreadingManagement,
  DigestateSaleTypeEnum as DigestateSaleType,
} from "api-schema"
import { apiTypes } from "common/services/api-fetch.types"

export {
  TariffReference,
  InstallationCategory,
  UnitType,
  HygienizationExemptionType,
  IcpeRegime,
  ProcessType,
  MethanizationProcess,
  DigestateValorizationMethod,
  SpreadingManagement,
  DigestateSaleType,
}

// Contracts
export type BiomethaneContract = apiTypes["BiomethaneContract"]
export type BiomethaneContractPatchRequest =
  apiTypes["BiomethaneContractPatchRequest"]

// Amendments
export type BiomethaneContractAmendment =
  apiTypes["BiomethaneContractAmendment"]
export type BiomethaneAmendmentAddRequest =
  apiTypes["BiomethaneContractAmendmentAddRequest"]

// Production Unit
export type BiomethaneProductionUnit = apiTypes["BiomethaneProductionUnit"]
export type BiomethaneProductionUnitAddRequest =
  apiTypes["BiomethaneProductionUnitAddRequest"]
export type BiomethaneProductionUnitPatchRequest =
  apiTypes["PatchedBiomethaneProductionUnitPatchRequest"]

// Digestate Storage
export type BiomethaneDigestateStorage = apiTypes["BiomethaneDigestateStorage"]
export type BiomethaneDigestateStorageAddRequest =
  apiTypes["BiomethaneDigestateStorageAddRequest"]
export type BiomethaneDigestateStoragePatchRequest =
  apiTypes["PatchedBiomethaneDigestateStoragePatchRequest"]
