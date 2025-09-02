import {
  CompostingLocationsEnum as BiomethaneDigestateCompostingLocation,
  BiomethaneDigestateStatusEnum as BiomethaneDigestateStatus,
} from "api-schema"
import { apiTypes } from "common/services/api-fetch.types"

export type BiomethaneDigestate = apiTypes["BiomethaneDigestate"]
export type BiomethaneDigestateInputRequest =
  apiTypes["BiomethaneDigestateInputRequest"]

export type BiomethaneDigestateSpreading =
  apiTypes["BiomethaneDigestateSpreading"]
export type BiomethaneDigestateSpreadingAddRequest =
  apiTypes["BiomethaneDigestateSpreadingAddRequest"]

export { BiomethaneDigestateCompostingLocation, BiomethaneDigestateStatus }
