import { useTranslation } from "react-i18next"
import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { getRediiThresholdLabel } from "../../contract.utils"
import { TariffReference } from "biomethane/pages/contract/types"

interface RedIIDialogProps {
  onClose: () => void
  onConfirm: (is_red_ii: boolean) => void
  tariffReference?: TariffReference | null
}

export const RedIIDialog = ({
  onClose,
  onConfirm,
  tariffReference,
}: RedIIDialogProps) => {
  const { t } = useTranslation()

  const handleConfirm = (is_red_ii: boolean) => {
    onConfirm(is_red_ii)
    onClose()
  }

  return (
    <Dialog
      onClose={onClose}
      header={
        <Dialog.Title>
          {t("Capacité maximale de production contractualisée")}
        </Dialog.Title>
      }
      footer={
        <>
          <Button priority="secondary" onClick={() => handleConfirm(false)}>
            {t("Non")}
          </Button>
          <Button onClick={() => handleConfirm(true)}>{t("Oui")}</Button>
        </>
      }
    >
      {t(
        "Votre capacité maximale de production contractualisée est inférieure à {{value}}, voulez-vous rester soumis aux exigences RED ?",
        { value: getRediiThresholdLabel(tariffReference) }
      )}
    </Dialog>
  )
}
