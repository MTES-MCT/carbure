import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Edit, Return } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { LotUpdateManyQuery } from "controls/types"
import { useTranslation } from "react-i18next"
import { Lot } from "transactions/types"

export interface UpdateManyButtonProps {
  disabled?: boolean
  pinned?: boolean
  selection: number[]
  lots: Lot[]
}

export const UpdateManyButton = ({
  disabled,
  selection,
  lots,
}: UpdateManyButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      disabled={disabled || selection.length === 0}
      variant="warning"
      icon={Edit}
      label={t("Modifier la séléction") } // prettier-ignore
      action={() =>
        portal((close) => (
          // update dialog
          <UpdateDialog onClose={close} />
        ))
      }
    />
  )
}

interface UpdateDialogProps {
  onClose: () => void
}
const UpdateDialog = ({ onClose }: UpdateDialogProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  const showValidation = () => {
    const query = {
      lots_ids: [],
      values: [],
      entities_to_notify: [],
    }

    portal((close) => (
      // update dialog
      <UpdateValidationDialog onClose={close} query={query} />
    ))
  }

  return (
    <Dialog onClose={onClose} fullscreen>
      <header>
        <h1>Vous êtes en train de modifer 15 lots</h1>
      </header>
      <main>
        <section>
          <p>
            Afin de modifier une valeur sur l’intégralité des lots sélectionnés,
            remplissez le champs souhaité.
          </p>
        </section>
      </main>

      <footer>
        <Button variant="warning" icon={Edit} action={showValidation}>
          {t("Modifier")}
        </Button>

        <Button icon={Return} action={onClose}>
          {t("Retour")}
        </Button>
      </footer>
    </Dialog>
  )
}

interface UpdateValidationDialogProps {
  onClose: () => void
  query: LotUpdateManyQuery
}
const UpdateValidationDialog = ({
  onClose,
  query,
}: UpdateValidationDialogProps) => {
  const { t } = useTranslation()

  const showValidation = () => {}

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>15 lots vont être modifiés</h1>
      </header>
      <main>
        <section>
          <p>Êtes vous sûr ?</p>
        </section>
      </main>

      <footer>
        <Button variant="warning" icon={Edit} action={showValidation}>
          {t("Modifier les 15 lots")}
        </Button>

        <Button icon={Return} action={onClose}>
          {t("Annuler")}
        </Button>
      </footer>
    </Dialog>
  )
}

export default UpdateManyButton
