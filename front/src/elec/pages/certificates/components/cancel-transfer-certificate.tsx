import { Button } from "common/components/button2"
import { useMutation } from "common/hooks/async"
import { cancelTransferCertificate } from "../api"
import { useTranslation } from "react-i18next"
import useEntity from "common/hooks/entity"
import { Dialog } from "common/components/dialog2"
import { usePortal } from "common/components/portal"
import { useNotify } from "common/components/notifications"

type CancelTransferCertificateProps = {
  id: number
}

export const CancelTransferCertificate = ({
  id,
}: CancelTransferCertificateProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  function showDialog() {
    portal((close) => (
      <CancelTransferCertificateDialog id={id} onClose={close} />
    ))
  }

  return (
    <Button
      iconId="fr-icon-close-line"
      customPriority="danger"
      onClick={showDialog}
    >
      {t("Annuler")}
    </Button>
  )
}

type CancelTransferCertificateDialogProps = {
  id: number
  onClose: () => void
}

const CancelTransferCertificateDialog = ({
  id,
  onClose,
}: CancelTransferCertificateDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()

  const entity = useEntity()

  const cancelResponse = useMutation(cancelTransferCertificate, {
    invalidates: [
      "elec-transfer-certificates",
      "elec-certificates-snapshot",
      "transfer-certificate-details",
      "years",
    ],
    onSuccess() {
      notify(t("Le certificat a bien été annulé"), { variant: "success" })
      onClose()
    },
    onError() {
      notify(t("Le certificat n'a pas pu être annulé"), { variant: "danger" })
      onClose()
    },
  })

  function onCancel() {
    cancelResponse.execute(entity.id, id)
  }

  return (
    <Dialog
      onClose={onClose}
      header={<Dialog.Title>{t("Annuler le certificat")}</Dialog.Title>}
      footer={
        <>
          <Button priority="secondary" onClick={onClose}>
            {t("Annuler")}
          </Button>
          <Button
            iconId="fr-icon-close-line"
            customPriority="danger"
            onClick={onCancel}
          >
            {t("Confirmer")}
          </Button>
        </>
      }
    >
      <p>{t("Voulez-vous annuler ce certificat de cession ?")}</p>
    </Dialog>
  )
}
