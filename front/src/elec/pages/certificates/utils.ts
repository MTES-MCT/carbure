import i18next from "i18next"
import { ProvisionCertificate, ProvisionCertificateSource } from "./types"
import { HttpError } from "common/services/api-fetch"

type ProvisionPeriodFields = Pick<
  ProvisionCertificate,
  "source" | "quarter" | "year" | "month"
>

export function isEnrRatioCompensation(
  source: ProvisionCertificate["source"] | null | undefined
) {
  return source === ProvisionCertificateSource.ENR_RATIO_COMPENSATION
}

export function formatProvisionQuarterCell(certificate: ProvisionPeriodFields) {
  if (isEnrRatioCompensation(certificate.source)) {
    return certificate.year == null ? "-" : String(certificate.year)
  }

  return i18next.t("T{{quarter}} {{year}}", {
    quarter: certificate.quarter,
    year: certificate.year,
  })
}

export function formatProvisionMonthCell(certificate: ProvisionPeriodFields) {
  if (isEnrRatioCompensation(certificate.source)) {
    return "-"
  }

  return i18next.t("{{month}}", {
    month: certificate.month ?? i18next.t("-"),
  })
}

export function formatProvisionPeriodLabel(
  source: ProvisionCertificate["source"] | null | undefined
) {
  return isEnrRatioCompensation(source)
    ? i18next.t("Année")
    : i18next.t("Trimestre")
}

export function shouldShowProvisionOperatingUnit(
  source: ProvisionCertificate["source"] | null | undefined
) {
  return !isEnrRatioCompensation(source)
}

export function shouldShowProvisionPeriod(
  source: ProvisionCertificate["source"] | null | undefined,
  month?: ProvisionCertificate["month"] | null
) {
  return !isEnrRatioCompensation(source) && !!month
}

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
    case ProvisionCertificateSource.ENR_RATIO_COMPENSATION:
      return i18next.t("Compensation ENR")
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
