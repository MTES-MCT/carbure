import { Button } from "common/components/button2"
import { useMutation } from "common/hooks/async"
import { rejectTransferCertificate } from "../api"
import { useTranslation } from "react-i18next"
import useEntity from "common/hooks/entity"
import { Dialog } from "common/components/dialog2"
import { usePortal } from "common/components/portal"
import { useForm } from "common/components/form"
import { useNotify } from "common/components/notifications"
import { TextInput } from "common/components/inputs2"

type RejectTransferCertificateProps = {
  id: number
}

export const RejectTransferCertificate = ({
  id,
}: RejectTransferCertificateProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  function showDialog() {
    portal((close) => (
      <RejectTransferCertificateDialog id={id} onClose={close} />
    ))
  }

  return (
    <Button
      iconId="fr-icon-close-line"
      customPriority="danger"
      onClick={showDialog}
    >
      {t("Refuser")}
    </Button>
  )
}

type RejectTransferCertificateDialogProps = {
  id: number
  onClose: () => void
}

const RejectTransferCertificateDialog = ({
  id,
  onClose,
}: RejectTransferCertificateDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()

  const entity = useEntity()

  const form = useForm({
    comment: undefined as string | undefined,
  })

  const rejectResponse = useMutation(rejectTransferCertificate, {
    invalidates: [
      "elec-transfer-certificates",
      "elec-certificates-snapshot",
      "transfer-certificate-details",
      "years",
    ],
    onSuccess() {
      notify(t("Le certificat a bien été refusé"), { variant: "success" })
      onClose()
    },
    onError() {
      notify(t("Le certificat n'a pas pu être refusé"), { variant: "danger" })
      onClose()
    },
  })

  function onReject() {
    rejectResponse.execute(entity.id, id, form.value.comment ?? "")
  }

  return (
    <Dialog
      onClose={onClose}
      header={<Dialog.Title>{t("Refuser le certificat")}</Dialog.Title>}
      footer={
        <>
          <Button priority="secondary" onClick={onClose}>
            {t("Annuler")}
          </Button>
          <Button
            iconId="fr-icon-close-line"
            customPriority="danger"
            onClick={onReject}
          >
            {t("Confirmer")}
          </Button>
        </>
      }
    >
      <p>
        <b>{t("Pour quelle raison refusez-vous ce certificat de cession ?")}</b>
      </p>
      <p>
        {t(
          "Cela entraînera la suppression du certificat. Le déclarant sera notifié de votre refus et le certificat ne sera plus visible parmi vos certificats de cession."
        )}
      </p>
      <TextInput
        required
        label={t("Commentaire")}
        placeholder={t("Entrez un commentaire")}
        {...form.bind("comment")}
      />
    </Dialog>
  )
}
