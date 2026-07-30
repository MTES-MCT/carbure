import { apiTypes } from "common/services/api-fetch.types"
import {
  AccessTypeEnum as AccessType,
  DistributedPressureEnum as DistributedPressure,
} from "api-schema"

export { AccessType, DistributedPressure }

export type H2Station = apiTypes["H2Station"]
export type H2StationInputRequest = apiTypes["H2StationInputRequest"]
