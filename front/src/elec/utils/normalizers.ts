import { ElecProvisionCertificateSource } from "../types"

/**
 * Get the i18next key of the source of a provision certificate
 * @param source - The source of the provision certificate
 * @returns The i18next key of the source
 */
export const getElecProvisionCertificateSourceLabel = (
  source: string | undefined
) => {
  switch (source) {
    case ElecProvisionCertificateSource.MANUAL:
      return "Manuel"
    case ElecProvisionCertificateSource.METER_READINGS:
      return "Relevés trimestriels"
    case ElecProvisionCertificateSource.QUALICHARGE:
      return "Qualicharge"
    default:
      return "N/A"
  }
}
