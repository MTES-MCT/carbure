import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { Plus, Return } from "common/components/icons"
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
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Remplacer le dossier existant")}</h1>
      </header>

      <main>
        <p>
          {t(
            "Le dossier que vous souhaitez ajouter existe déjà. Voulez-vous le remplacer ?"
          )}
        </p>
      </main>

      <footer>
        <Button
          icon={Plus}
          label={t("Remplacer le dossier")}
          variant="primary"
          action={replaceApplication}
        />

        <Button icon={Return} label={t("Annuler")} action={onClose} asideX />
      </footer>
    </Dialog>
  )
}
