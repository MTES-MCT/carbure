import {
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
  UnitType,
  HygienizationExemptionType,
  IcpeRegime,
  ProcessType,
  MethanizationProcess,
  DigestateValorizationMethod,
  SpreadingManagement,
  DigestateSaleType,
}

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
