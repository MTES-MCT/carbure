import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Cross, Return } from "common/components/icons"
import { TextInput } from "common/components/input"
import { useMutation } from "common/hooks/async"
import { formatDate } from "common/utils/formatters"
import * as api from "elec/api"
import { ElecTransferCertificatePreview } from "elec/types"
import { useTranslation } from "react-i18next"
import TransferCertificateTag from "./tag"

export interface ElectTransferDetailsDialogProps {
  onClose: () => void
  transfer_certificate: ElecTransferCertificatePreview
  onTransferCancelled: (volume: number, clientName: string) => void
}
export const ElectTransferDetailsDialog = ({
  onClose,
  transfer_certificate,
  onTransferCancelled
}: ElectTransferDetailsDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const cancelTransferEnergyRequest = useMutation(api.cancelTransferCertificate, {
    invalidates: [
      "elec-transfer-certificates",
      "elec-cpo-snapshot"
    ],
    onSuccess: () => {
      onTransferCancelled(transfer_certificate.energy_amount!, transfer_certificate.client!.name)
      onClose()
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
          <TextInput
            readOnly
            label={t("Redevable")}
            value={transfer_certificate.client.name}

          />
          <TextInput
            readOnly
            label={t("MWh")}
            value={transfer_certificate.energy_amount + " MWh"}

          />


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

export default ElectTransferDetailsDialog
