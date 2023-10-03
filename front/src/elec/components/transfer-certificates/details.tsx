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
import Portal, { usePortal } from "common/components/portal"
import { AcceptTransfer } from "./accept"
import Alert from "common/components/alert"
import { useLocation, useNavigate } from "react-router-dom"
import { useHashMatch } from "common/components/hash-route"
import { useQuery } from "common/hooks/async"
import * as apiOperator from "../../api-operator"
import * as apiCPO from "../../api-cpo"
export interface ElecTransferDetailsDialogProps {
  displayCpo?: boolean
}
export const ElecTransferDetailsDialog = ({
  displayCpo,
}: ElecTransferDetailsDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const portal = usePortal()
  const navigate = useNavigate()
  const location = useLocation()
  const match = useHashMatch("transfer-certificate/:id")

  const api = displayCpo ? apiCPO : apiOperator

  const transferCertificateResponse = useQuery(api.getTransferCertificateDetails, {
    key: "transfer-certificate-details",
    params: [entity.id, parseInt(match?.params.id!)],
  })
  const transferCertificate = transferCertificateResponse.result?.data.data?.elec_transfer_certificate


  const showRejectModal = () => {
    portal((close) => <RejectTransfer transferCertificate={transferCertificate} onClose={close} onRejected={closeDialog} />)
  }

  const showAcceptModal = async () => {
    portal((close) => <AcceptTransfer transferCertificate={transferCertificate} onClose={close} onAccepted={closeDialog} />)
  }

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog} >
        <header>
          <TransferCertificateTag status={transferCertificate?.status} big />
          <h1>
            {t("Certificat de cession n°{{id}}", { id: transferCertificate?.certificate_id || "-" })}
          </h1>
        </header>

        <main>
          <section>
            <TextInput
              readOnly
              label={t("Date d'émission")}
              value={transferCertificate && formatDate(transferCertificate.transfer_date)}

            />
            {displayCpo ?
              <TextInput
                readOnly
                label={t("Aménageur")}
                value={transferCertificate?.supplier.name}

              />
              : <TextInput
                readOnly
                label={t("Redevable")}
                value={transferCertificate?.client.name}

              />
            }

            <TextInput
              readOnly
              label={t("MWh")}
              value={transferCertificate?.energy_amount + " MWh"}

            />
            {transferCertificate?.status === ElecOperatorStatus.Accepted && entity.id === transferCertificate?.client.id &&
              <Alert variant="info" icon={Message}>
                {t("L'identifiant est à reporter sur le certificat d'acquisition à intégrer dans votre comptabilité matière pour le compte des douanes.")}
              </Alert>
            }
          </section>

        </main>

        <footer>
          {transferCertificate?.status === ElecOperatorStatus.Pending &&
            transferCertificate?.client.id === entity.id && (
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
          {entity.id === transferCertificate?.supplier.id &&
            <ElecCancelTransferButton
              transferCertificate={transferCertificate}
              onClose={closeDialog}
            />
          }
          <Button icon={Return} label={t("Retour")} action={closeDialog} />
        </footer>
      </Dialog>
    </Portal>
  )
}

export default ElecTransferDetailsDialog
