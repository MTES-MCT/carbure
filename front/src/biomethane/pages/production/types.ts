import {
  UnitTypeEnum as UnitType,
  HygienizationExemptionTypeEnum as HygienizationExemptionType,
  IcpeRegimeEnum as IcpeRegime,
  ProcessTypeEnum as ProcessType,
  MethanizationProcessEnum as MethanizationProcess,
  DigestateValorizationMethodsEnum as DigestateValorizationMethods,
  SpreadingManagementMethodsEnum as SpreadingManagementMethods,
  DigestateSaleTypesEnum as DigestateSaleTypes,
  InstalledMetersEnum as InstalledMeters,
} from "api-schema"
import { apiTypes } from "common/services/api-fetch.types"
import { DeepPartial } from "common/types"

export {
  UnitType,
  HygienizationExemptionType,
  IcpeRegime,
  ProcessType,
  MethanizationProcess,
  DigestateValorizationMethods,
  SpreadingManagementMethods,
  DigestateSaleTypes,
  InstalledMeters,
}

// Production Unit

export type BiomethaneProductionUnit = apiTypes["BiomethaneProductionUnit"]
export type BiomethaneProductionUnitPatchRequest =
  apiTypes["BiomethaneProductionUnitUpsertRequest"]
export type ProductionUnitForm =
  DeepPartial<BiomethaneProductionUnitPatchRequest>

// Digestate Storage

export type BiomethaneDigestateStorage = apiTypes["BiomethaneDigestateStorage"]
export type BiomethaneDigestateStorageInputRequest =
  apiTypes["BiomethaneDigestateStorageInputRequest"]
