import { HttpResponse } from "msw"
import { http } from "common/__test__/http"
import { ProvisionCertificate } from "../types"
import {
  provisionCertificateEnrCompensation,
  provisionCertificateMeterReadings,
} from "./data"

export const generateGetProvisionCertificateDetails = (
  provisionCertificate: ProvisionCertificate
) =>
  http.get("/elec/provision-certificates/{id}/", () =>
    HttpResponse.json(provisionCertificate)
  )

export const okGetProvisionCertificateMeterReadingsDetails =
  generateGetProvisionCertificateDetails(provisionCertificateMeterReadings)

export const okGetProvisionCertificateEnrCompensationDetails =
  generateGetProvisionCertificateDetails(provisionCertificateEnrCompensation)
