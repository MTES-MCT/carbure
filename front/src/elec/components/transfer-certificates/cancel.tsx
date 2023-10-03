import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Cross, Return } from "common/components/icons"
import { useNotify, useNotifyError } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import { useMutation } from "common/hooks/async"
import * as api from "elec/api-cpo"
import { ElecTransferCertificatePreview } from "elec/types"
import { useTranslation } from "react-i18next"


interface ElecCancelTransferButtonProps {
  transferCertificate: ElecTransferCertificatePreview
  onClose: () => void
}

export const ElecCancelTransferButton = ({ transferCertificate, onClose }: ElecCancelTransferButtonProps) => {
  const entity = useEntity()
  const { t } = useTranslation()
  const portal = usePortal()
  const notify = useNotify()

  const onTransferCancelledSuccess = (volume: number, clientName: string) => {
    notify(t("{{volume}} MWh initalement envoyés à {{clientName}} vous ont bien été restitués", { volume, clientName }), { variant: "success" })
    onClose()
  }


  const confirmCancelTransferCertificate = async () => {
    portal((close) => <ElecCancelTransferConfirmDialog onClose={close} onTransferCancelled={onTransferCancelledSuccess} transfer_certificate={transferCertificate} />)
  }

  return (
    <Button
      icon={Cross}
      label={t("Annuler le certificat de cession")}
      variant="danger"
      action={confirmCancelTransferCertificate}
    />
  );
};




export interface ElecCancelTransferConfirmDialogProps {
  onClose: () => void
  transfer_certificate: ElecTransferCertificatePreview
  onTransferCancelled: (volume: number, clientName: string) => void
}

export const ElecCancelTransferConfirmDialog = ({
  onClose,
  transfer_certificate,
  onTransferCancelled
}: ElecCancelTransferConfirmDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notifyError = useNotifyError()

  const cancelTransferEnergyRequest = useMutation(api.cancelTransferCertificate, {
    invalidates: [
      "elec-transfer-certificates",
      "elec-cpo-snapshot"
    ],
    onSuccess: () => {
      onTransferCancelled(transfer_certificate.energy_amount!, transfer_certificate.client!.name)
      onClose()
    },
    onError: (err) => {
      notifyError(err, t("Impossible d'annuler le certificat de cession"))
    }
  })

  const cancelTransferCertificate = async () => {
    await cancelTransferEnergyRequest.execute(
      entity.id,
      transfer_certificate.id,
    )
  }

  return (

    <Dialog onClose={onClose} >
      <header>

        <h1>
          {t("Annuler le certificat de cession n°{{id}}", { id: transfer_certificate.certificate_id })}
        </h1>
      </header>

      <main>
        <section>
          <p>
            <strong>Êtes-vous sûr de vouloir annuler ce certificat de cession ?</strong>
          </p>
          <p>Cela entrainera sa suppression et son volume en MWh sera à nouveau disponible dans votre stock d'énergie global.</p>



        </section>
      </main>

      <footer>
        <Button
          loading={cancelTransferEnergyRequest.loading}
          icon={Cross}
          label={t("Annuler le certificat de cession")}
          variant="danger"
          action={cancelTransferCertificate}
        />

        <Button icon={Return} label={t("Retour")} action={onClose} />
      </footer>
    </Dialog>

  )
}

