import api, { Api } from "common/services/api"
import {
  DoubleCountingApplicationOverview,
  DoubleCountingApplicationDetails,
  DoubleCountingFileInfo,
  DoubleCountingUploadErrors,
  QuotaDetails,
  AgreementDetails
} from "double-counting/types"

export function getDoubleCountingAgreements(entity_id: number) {
  return api.get<Api<DoubleCountingApplicationOverview[]>>("/double-counting/agreements", {
    params: { entity_id },
  })
}

export function getDoubleCountingApplicationDetails(entity_id: number, dca_id: number) {
  return api.get<Api<DoubleCountingApplicationDetails>>(
    "/double-counting/applications/details",
    {
      params: { entity_id, dca_id },
    }
  )
}


export function checkDoubleCountingApplication(entity_id: number, file: File) {
  const res = api.post<Api<{ file: DoubleCountingFileInfo }>>(
    "/double-counting/applications/check-file",
    { entity_id, file }
  )
  return res
}

export function getDoubleCountingAgreementDetails(entity_id: number, agreement_id: number) {
  return api.get<Api<AgreementDetails>>(
    "/double-counting/agreements/details",
    {
      params: { entity_id, agreement_id },
    }
  )
}

