import {
  UnitTypeEnum as UnitType,
  HygienizationExemptionTypeEnum as HygienizationExemptionType,
  IcpeRegimeEnum as IcpeRegime,
  ProcessTypeEnum as ProcessType,
  MethanizationProcessEnum as MethanizationProcess,
  DigestateValorizationMethodsEnum as DigestateValorizationMethods,
  SpreadingManagementMethodsEnum as SpreadingManagementMethods,
  DigestateSaleTypeEnum as DigestateSaleType,
  InstalledMetersEnum as InstalledMeters,
} from "api-schema"
import { apiTypes } from "common/services/api-fetch.types"

export {
  UnitType,
  HygienizationExemptionType,
  IcpeRegime,
  ProcessType,
  MethanizationProcess,
  DigestateValorizationMethods,
  SpreadingManagementMethods,
  DigestateSaleType,
  InstalledMeters,
}

// Production Unit

export type BiomethaneProductionUnit = apiTypes["BiomethaneProductionUnit"]
export type BiomethaneProductionUnitPatchRequest =
  apiTypes["BiomethaneProductionUnitUpsertRequest"]

// Digestate Storage

export type BiomethaneDigestateStorage = apiTypes["BiomethaneDigestateStorage"]
export type BiomethaneDigestateStorageAddRequest =
  apiTypes["BiomethaneDigestateStorageAddRequest"]
export type BiomethaneDigestateStoragePatchRequest =
  apiTypes["PatchedBiomethaneDigestateStoragePatchRequest"]
