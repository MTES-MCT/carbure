import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Edit, Return } from "common/components/icons"
import { usePortal } from "common/components/portal"
import LotForm, { useLotForm } from "lot-add/components/lot-form"
import { useTranslation } from "react-i18next"
import { Lot } from "transactions/types"
import UpdateConfirmationDialog from "./update-confirmation"

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
      label={t("Modifier la séléction")}
      action={() =>
        portal((close) => <UpdateDialog onClose={close} lots={lots} />)
      }
    />
  )
}

interface UpdateDialogProps {
  onClose: () => void
  lots: Lot[]
}
const UpdateDialog = ({ onClose, lots }: UpdateDialogProps) => {
  const { t } = useTranslation()
  const portal = usePortal()
  const form = useLotForm()

  const showValidation = () => {
    // const editedValue = Object.keys(form.value).filter(
    //   (key) => form.value?.[key] !== defaultLot[key]
    // )

    portal((close) => (
      <UpdateConfirmationDialog onClose={close} lots={lots} value={"biofuel"} />
    ))
  }

  return (
    <Dialog onClose={onClose} fullscreen>
      <header>
        <h1>
          {t("Modification de {{lotCount}} lots", {
            lotCount: lots.length,
          })}
        </h1>
      </header>
      <main>
        <section>
          <p>
            {t(
              "Afin de modifier une valeur sur l’intégralité des lots sélectionnés, remplissez le champs souhaité."
            )}
          </p>
        </section>
        <section>
          <LotForm form={form} />
        </section>
      </main>

      <footer>
        <Button
          variant="warning"
          icon={Edit}
          action={showValidation}
          submit="lot-form"
        >
          {t("Modifier")}
        </Button>

        <Button asideX icon={Return} action={onClose}>
          {t("Retour")}
        </Button>
      </footer>
    </Dialog>
  )
}

export default UpdateManyButton
