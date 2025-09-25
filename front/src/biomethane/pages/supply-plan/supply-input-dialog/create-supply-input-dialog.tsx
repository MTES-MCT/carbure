import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { useTranslation } from "react-i18next"
import { SupplyInputForm } from "./supply-input-form"

export const CreateSupplyInputDialog = ({
  onClose,
}: {
  onClose: () => void
}) => {
  const { t } = useTranslation()
  return (
    <Dialog
      header={<Dialog.Title>{t("Ajouter un intrant")}</Dialog.Title>}
      footer={<Button>{t("Valider l'intrant")}</Button>}
      onClose={onClose}
      size="large"
    >
      <SupplyInputForm />
    </Dialog>
  )
}
