import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Edit, Return } from "common/components/icons"
import { usePortal } from "common/components/portal"
import LotForm, {
  defaultLot,
  LotFormValue,
  useLotForm,
} from "lot-add/components/lot-form"
import { useTranslation } from "react-i18next"
import { Lot } from "transactions/types"
import UpdateConfirmationDialog from "./update-many-confirmation"

export interface UpdateManyButtonProps {
  disabled?: boolean
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

  let updatedValues: Partial<LotFormValue> = {}
  Object.keys(form.value).forEach((_key) => {
    const key = _key as keyof LotFormValue
    if (form.value[key] !== defaultLot[key] && form.value[key] !== "") {
      ; (updatedValues as any)[key] = form.value[key]
    }
  })

  const showValidation = () => {
    portal((close) => (
      <UpdateConfirmationDialog
        onClose={close}
        onSuccess={() => {
          close()
          onClose()
        }}
        lots={lots}
        updatedValues={updatedValues}
      />
    ))
  }

  return (
    <Dialog onClose={onClose} fullscreen>
      <header>
        <h1>
          {t("Modification de {{count}} lots", {
            count: lots.length,
          })}
        </h1>
      </header>
      <main>
        <section>
          <p>
            {t(
              "Remplissez les champs que vous souhaitez modifier sur l'intégralité des lots sélectionnés."
            )}
          </p>
        </section>
        <section>
          <LotForm form={form} novalidate />
        </section>
      </main>

      <footer>
        <Button
          variant="warning"
          icon={Edit}
          action={showValidation}
          submit="lot-form"
          disabled={!Object.keys(updatedValues).length}
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
