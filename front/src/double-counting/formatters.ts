import { AgreementRegistrationStatus } from "./types"

export const getAgreementRegistrationStatusLabel = (
  status: AgreementRegistrationStatus,
  t: (key: string) => string
) => {
  const statusLabels = {
    [AgreementRegistrationStatus.VALID]: t("Valide"),
    [AgreementRegistrationStatus.SUSPENDED]: t("Suspendu"),
    [AgreementRegistrationStatus.WITHDRAWN]: t("Retiré"),
    [AgreementRegistrationStatus.TERMINATED]: t("Interrompu"),
  }

  return statusLabels[status]
}
