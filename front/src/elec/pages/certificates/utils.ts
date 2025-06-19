import i18next from "i18next"
import { ProvisionCertificateSource } from "./types"
import { HttpError } from "common/services/api-fetch"

export function normalizeSource(source: string) {
  return {
    value: source,
    label: getSourceLabel(source),
  }
}

export function getSourceLabel(source: string | null | undefined) {
  switch (source) {
    case ProvisionCertificateSource.MANUAL:
      return i18next.t("DGEC")
    case ProvisionCertificateSource.METER_READINGS:
      return i18next.t("Relevés trimestriels")
    case ProvisionCertificateSource.QUALICHARGE:
      return i18next.t("Qualicharge")
    default:
      return i18next.t("N/A")
  }
}

export function getTransferErrorLabel(error: Error) {
  const errorCode = (error as HttpError)?.data?.detail
  switch (errorCode) {
    case "NOT_ENOUGH_ENERGY":
      return i18next.t("Pas assez d'énergie disponible")
    default:
      return errorCode
  }
}
