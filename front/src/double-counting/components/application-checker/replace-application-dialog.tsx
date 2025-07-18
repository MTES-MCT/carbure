import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { useTranslation } from "react-i18next"

export type ReplaceApplicationDialogProps = {
  onClose: () => void
  onReplace: (shouldReplace: boolean) => void
  loading?: boolean
}

export const ReplaceApplicationDialog = ({
  onReplace,
  onClose,
}: ReplaceApplicationDialogProps) => {
  const { t } = useTranslation()

  const replaceApplication = async () => {
    onReplace(true)
    onClose()
  }

  return (
    <Dialog
      onClose={onClose}
      header={<Dialog.Title>{t("Remplacer le dossier existant")}</Dialog.Title>}
      footer={
        <Button iconId="fr-icon-add-line" onClick={replaceApplication}>
          {t("Remplacer le dossier")}
        </Button>
      }
    >
      {t(
        "Le dossier que vous souhaitez ajouter existe déjà. Voulez-vous le remplacer ?"
      )}
    </Dialog>
  )
}
