import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Cross, Return } from "common/components/icons"
import { useNotify } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import TransferCertificateTag from "elec/components/transfer-certificates/tag"
import { ElecTransferCertificatesDetails } from "elec/types"
import { useTranslation } from "react-i18next"
import * as api from "../../api-operator"

interface AcceptTransferProps {
  transferCertificate?: ElecTransferCertificatesDetails
  onClose: () => void
  onAccepted: () => void
}

export const AcceptTransfer = ({
  transferCertificate,
  onClose,
  onAccepted,
}: AcceptTransferProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()

  const acceptTransfer = useMutation(api.acceptTransfer, {
    invalidates: [
      "elec-transfer-certificates",
      "elec-operator-snapshot",
      `nav-stats-${entity.id}`,
    ],
    onSuccess: () => {
      notify(t("Le certificat de cession a été accepté"), {
        variant: "success",
      })
      onAccepted()
      onClose()
    },
  })

  const onAcceptTransfer = async () => {
    await acceptTransfer.execute(entity.id, transferCertificate!.id)
  }

  return (
    <Dialog onClose={onClose}>
      <header>
        <TransferCertificateTag status={transferCertificate?.status} />

        <h1>
          {t("Accepter le certificat de cession n°")}
          {transferCertificate?.certificate_id ?? "..."}
        </h1>
      </header>

      <main>
        <section>
          <p>
            {t(
              "En acceptant ce certificat de cession, vous pourrez le retrouver dans la section Certificats acceptés."
            )}
          </p>
        </section>
      </main>

      <footer>
        <Button
          icon={Cross}
          label={t("Accepter")}
          variant="primary"
          disabled={!transferCertificate}
          action={onAcceptTransfer}
        />

        <Button icon={Return} label={t("Retour")} action={onClose} />
      </footer>
    </Dialog>
  )
}
