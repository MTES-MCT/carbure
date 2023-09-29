import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Check, Cross, Message, Return } from "common/components/icons"
import { TextInput } from "common/components/input"
import { formatDate } from "common/utils/formatters"
import { ElecTransferCertificatePreview } from "elec/types"
import { useTranslation } from "react-i18next"
import TransferCertificateTag from "./tag"
import { ElecCancelTransferButton } from "./cancel"
import { ElecOperatorStatus } from "elec/types-operator"
import { RejectTransfer } from "./reject"
import { usePortal } from "common/components/portal"
import { AcceptTransfer } from "./accept"
import Alert from "common/components/alert"

export interface ElecTransferDetailsDialogProps {
  onClose: () => void
  displayCpo?: boolean
  transfer_certificate: ElecTransferCertificatePreview
}
export const ElecTransferDetailsDialog = ({
  onClose,
  displayCpo,
  transfer_certificate,
}: ElecTransferDetailsDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const portal = usePortal()



  const showRejectModal = () => {
    portal((close) => <RejectTransfer transfer_certificate={transfer_certificate} onClose={close} onRejected={onClose} />)
  }

  const showAcceptModal = async () => {
    portal((close) => <AcceptTransfer transfer_certificate={transfer_certificate} onClose={close} onAccepted={onClose} />)

  }
  return (

    <Dialog onClose={onClose} >
      <header>
        <TransferCertificateTag status={transfer_certificate.status} big />
        <h1>
          {t("Certificat de cession n°{{id}}", { id: transfer_certificate.certificate_id })}
        </h1>
      </header>

      <main>
        <section>
          <TextInput
            readOnly
            label={t("Date d'émission")}
            value={formatDate(transfer_certificate.transfer_date)}

          />
          {displayCpo ?
            <TextInput
              readOnly
              label={t("Aménageur")}
              value={transfer_certificate.supplier.name}

            />
            : <TextInput
              readOnly
              label={t("Redevable")}
              value={transfer_certificate.client.name}

            />
          }

          <TextInput
            readOnly
            label={t("MWh")}
            value={transfer_certificate.energy_amount + " MWh"}

          />
          {transfer_certificate.status === ElecOperatorStatus.Accepted &&
            <Alert variant="info" icon={Message}>
              {t("L’identifiant est à reporter sur le certificat d'acquisition à intégrer dans votre comptabilité matière pour le compte des douanes.")}
            </Alert>
          }
        </section>

      </main>

      <footer>
        {transfer_certificate?.status === ElecOperatorStatus.Pending &&
          transfer_certificate?.client.id === entity.id && (
            <>
              <Button
                icon={Check}
                label={t("Accepter")}
                variant="success"
                action={showAcceptModal}
              />
              <Button
                icon={Cross}
                label={t("Refuser")}
                variant="danger"
                action={showRejectModal}
              />
            </>
          )}
        {entity.id === transfer_certificate.supplier.id &&
          <ElecCancelTransferButton
            transfer_certificate={transfer_certificate}
            onClose={onClose}
          />
        }
        <Button icon={Return} label={t("Retour")} action={onClose} />
      </footer>
    </Dialog>

  )
}

export default ElecTransferDetailsDialog
