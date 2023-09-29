import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Return } from "common/components/icons"
import { TextInput } from "common/components/input"
import { formatDate } from "common/utils/formatters"
import { ElecTransferCertificatePreview } from "elec/types"
import { useTranslation } from "react-i18next"
import TransferCertificateTag from "../../../elec-admin/components/transfer-certificate/tag"
import { ElecCancelTransferButton } from "./cancel"

export interface ElectTransferDetailsDialogProps {
  onClose: () => void
  transfer_certificate: ElecTransferCertificatePreview
}
export const ElectTransferDetailsDialog = ({
  onClose,
  transfer_certificate,
}: ElectTransferDetailsDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()


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

export default ElectTransferDetailsDialog
