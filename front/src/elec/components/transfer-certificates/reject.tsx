import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import Form, { useForm } from "common/components/form"
import { Cross, Return } from "common/components/icons"
import { TextInput } from "common/components/input"
import { useNotify } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import TransferCertificateTag from "elec/components/transfer-certificates/tag"
import { ElecTransferCertificatesDetails } from "elec/types"
import { useTranslation } from "react-i18next"
import * as api from "../../api-operator"

interface RejectTransferProps {
  transferCertificate?: ElecTransferCertificatesDetails
  onClose: () => void
  onRejected: () => void
}

export const RejectTransfer = ({
  transferCertificate,
  onClose,
  onRejected,
}: RejectTransferProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()

  const { value, bind } = useForm<{ comment: string | undefined }>({
    comment: undefined,
  })

  const rejectTransfer = useMutation(api.rejectTransfer, {
    invalidates: [
      "elec-transfer-certificates",
      "elec-operator-snapshot",
      `nav-stats-${entity.id}`,
    ],
    onSuccess: () => {
      notify(
        t(
          "Le certificat de cession a été refusé et la raison mentionnée a été communiquée au fournisseur."
        ),
        { variant: "success" }
      )
      onRejected()
      onClose()
    },
  })

  const onRejectTransfer = async () => {
    await rejectTransfer.execute(
      entity.id,
      transferCertificate!.id,
      value.comment!
    )
  }

  return (
    <Dialog onClose={onClose}>
      <header>
        <TransferCertificateTag status={transferCertificate?.status} />

        <h1>
          {t("Refuser le certificat de cession n°")}
          {transferCertificate?.certificate_id ?? "..."}
        </h1>
      </header>

      <main>
        <section>
          <p>
            <strong>
              {t("Pour quelle raison refusez-vous ce certificat de cession ?")}
            </strong>{" "}
            {t(
              "Cela entraînera la suppression du certificat. Le déclarant sera notifié de votre refus et le certificat ne sera plus visible parmi vos certificats de cession."
            )}
          </p>
          <Form id="reject-transfer" onSubmit={onRejectTransfer}>
            <TextInput
              label={t("Commentaire")}
              required
              placeholder={t("Entrez un commentaire...")}
              {...bind("comment")}
            />
          </Form>
        </section>
      </main>

      <footer>
        <Button
          icon={Cross}
          label={t("Refuser")}
          variant="danger"
          disabled={!value.comment}
          submit="reject-transfer"
        />

        <Button icon={Return} label={t("Retour")} action={onClose} />
      </footer>
    </Dialog>
  )
}
