import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { useHashMatch } from "common/components/hash-route"
import { Message, Return } from "common/components/icons"
import { TextInput } from "common/components/input"
import Portal from "common/components/portal"
import { useQuery } from "common/hooks/async"
import { formatDate } from "common/utils/formatters"
import TransferCertificateTag from "elec/components/transfer-certificates/tag"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "../../api"
import { ElecTransferCertificateStatus } from "elec/types-cpo"
import Alert from "common/components/alert"

export const ElecAdminTransferDetailsDialog = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const navigate = useNavigate()
  const location = useLocation()
  const match = useHashMatch("transfer-certificate/:id")

  const transferCertificateResponse = useQuery(
    api.getTransferCertificateDetails,
    {
      key: "transfer-certificate-details",
      params: [entity.id, parseInt(match?.params.id || "")],
    }
  )
  const transferCertificate =
    transferCertificateResponse.result?.data.data?.elec_transfer_certificate

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog}>
        <header>
          <TransferCertificateTag status={transferCertificate?.status} big />
          <h1>
            {t("Certificat de cession n°{{id}}", {
              id: transferCertificate?.certificate_id,
            })}
          </h1>
        </header>

        <main>
          <section>
            <TextInput
              readOnly
              label={t("Date d'émission")}
              value={
                transferCertificate &&
                formatDate(transferCertificate.transfer_date)
              }
            />

            <TextInput
              readOnly
              label={t("Aménageur")}
              value={transferCertificate?.supplier.name}
            />
            <TextInput
              readOnly
              label={t("Redevable")}
              value={transferCertificate?.client.name}
            />

            <TextInput
              readOnly
              label={t("MWh")}
              value={transferCertificate?.energy_amount + " MWh"}
            />

            {transferCertificate?.status ===
              ElecTransferCertificateStatus.Rejected && (
              <Alert variant="info" icon={Message}>
                {transferCertificate.comment}
              </Alert>
            )}
          </section>
        </main>

        <footer>
          <Button icon={Return} label={t("Retour")} action={closeDialog} />
        </footer>
      </Dialog>
    </Portal>
  )
}

export default ElecAdminTransferDetailsDialog
