import { useTranslation } from "react-i18next"
import { EntityDepot } from "common/types"
import { Dialog } from "common/components/dialog2"
import { DeliverySiteForm } from "./create-delivery-site-form"

type DeliverySiteDialogProps = {
  deliverySite: EntityDepot
  onClose: () => void
}

export const DeliverySiteDialog = ({
  deliverySite,
  onClose,
}: DeliverySiteDialogProps) => {
  const { t } = useTranslation()

  return (
    <Dialog
      onClose={onClose}
      header={<Dialog.Title>{t("Détails du dépôt")}</Dialog.Title>}
    >
      <DeliverySiteForm
        formId="new-delivery-site"
        isReadOnly
        deliverySite={deliverySite}
      />
    </Dialog>
  )
}
