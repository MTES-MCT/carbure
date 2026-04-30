import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { FileCheck, Return } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { formatDate } from "common/utils/formatters"
import { LotCertificate } from "transaction-details/types"
import { useTranslation } from "react-i18next"
import i18next from "i18next"

interface CertificateProps {
  certificate: LotCertificate | undefined
}

export const CertificateIcon = ({ certificate }: CertificateProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  if (!certificate || !certificate.found) {
    return null
  }

  return (
    <Button
      captive
      icon={<FileCheck color="var(--gray-dark)" />}
      variant="icon"
      action={() =>
        portal((close) => (
          <Dialog onClose={close}>
            <header>
              <h1>{t("Détails du certificat")}</h1>
            </header>
            <main>
              <section>
                <ul style={{ whiteSpace: "pre-wrap" }}>
                  <li>
                    <b>{t("Type")}:</b>{" "}
                    <span>{certificate.certificate_type}</span>
                  </li>
                  <li>
                    <b>{t("Identifiant")}:</b>{" "}
                    <span>{certificate.certificate_id}</span>
                  </li>
                  <li>
                    <b>{t("Statut")}:</b>{" "}
                    <span>{getCertificateStatusLabel(certificate.status)}</span>
                  </li>
                  <li>
                    <b>{t("Détenteur")}:</b> <span>{certificate.holder}</span>
                  </li>
                  <li>
                    <b>{t("Validité")}:</b>{" "}
                    <span>
                      {formatDate(certificate.valid_from)}
                      {" → "}
                      {formatDate(certificate.valid_until)}
                    </span>
                  </li>
                </ul>
              </section>
            </main>
            <footer>
              <Button asideX icon={Return} label={t("Retour")} action={close} />
            </footer>
          </Dialog>
        ))
      }
    />
  )
}

function getCertificateStatusLabel(status: string) {
  switch (status) {
    case "PENDING":
      return i18next.t("En attente")
    case "VALID":
    case "ACTIVE":
    case "EXPIRES_SOON":
      return i18next.t("Valide")
    case "SUSPENDED":
      return i18next.t("Suspendu")
    case "WITHDRAWN":
      return i18next.t("Retiré")
    case "TERMINATED":
      return i18next.t("Interrompu")
    case "EXPIRED":
      return i18next.t("Expiré")
    default:
      return status
  }
}

export default CertificateIcon
