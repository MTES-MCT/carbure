import { mockGetWithResponseData, mockPostWithResponseData } from "carbure/__test__/helpers";
import { elecChargePointApplicationPending } from "elec/__test__/data";
import { elecChargePointsApplicationSample } from "./data";

export const okApplicationDetails = mockGetWithResponseData("/api/elec/admin/audit/charge-points/application-details", elecChargePointApplicationPending)
export const okGenerateSample = mockPostWithResponseData("/api/elec/admin/audit/charge-points/generate-sample", elecChargePointsApplicationSample)


