import Button from "common/components/button"
import Collapse from "common/components/collapse"
import Dialog from "common/components/dialog"
import { Edit } from "common/components/icons"
import { LotsUpdateError } from "controls/types"
import { useTranslation } from "react-i18next"

interface UpdateErrorsDialogProps {
  onClose: () => void
  errors: LotsUpdateError[]
}
export const UpdateErrorsDialog = ({
  onClose,
  errors,
}: UpdateErrorsDialogProps) => {
  const { t } = useTranslation()

  return (
    <Dialog onClose={onClose} fullscreen>
      <header>
        <h1>
          {t("{{count}} lots vont être modifiés.", {
            count: errors.length,
          })}
        </h1>
      </header>
      <main>
        <section>
          <p>
            <strong>
              {t("Les lots ci dessous n’ont pas pu être modifiés : ")}
            </strong>
          </p>

          {errors.map((error) => (
            <ErrorCollapse updateError={error} key={error.lot_id} />
          ))}
        </section>
      </main>

      <footer>
        <Button variant="primary" action={onClose}>
          {t("J'ai compris")}
        </Button>
      </footer>
    </Dialog>
  )
}

const ErrorCollapse = ({ updateError }: { updateError: LotsUpdateError }) => {
  const { t } = useTranslation()

  return (
    <Collapse
      icon={Edit}
      variant="warning"
      label={t("Lot #{{lotId}}", {
        lotId: updateError.lot_id,
      })}
      isOpen
    >
      <ul>
        {updateError.errors.map((error, index) => {
          return <li key={`${error.field}${index}`}>{error.error}</li>
        })}
      </ul>
      <footer></footer>
    </Collapse>
  )
}
