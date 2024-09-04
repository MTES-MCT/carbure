import Button from "common/components/button"
import Collapse from "common/components/collapse"
import Dialog from "common/components/dialog"
import { Edit } from "common/components/icons"
import { LotError } from "../../transactions/types"
import { useTranslation } from "react-i18next"
import { getAnomalyText } from "transaction-details/components/lots/anomalies"

interface UpdateErrorsDialogProps {
  onClose: () => void
  errors: { [key: number]: LotError[] }
  method: "update" | "delete"
}
export const UpdateErrorsDialog = ({
  onClose,
  errors,
  method,
}: UpdateErrorsDialogProps) => {
  const { t } = useTranslation()

  const errorsKeys = Object.keys(errors)
  return (
    <Dialog onClose={onClose} fullscreen>
      <header>
        <h1>
          {method === "update"
            ? t("{{count}} lots n'ont pas pu être modifiés :", {
                count: errorsKeys.length,
              })
            : t("{{count}} lots n'ont pas pu être supprimés :", {
                count: errorsKeys.length,
              })}
        </h1>
      </header>
      <main>
        <section>
          <p>
            <strong>
              {method === "update"
                ? t("Les lots ci-dessous n'ont pas pu être modifiés : ")
                : t("Les lots ci-dessous n'ont pas pu être supprimés : ")}
            </strong>
          </p>

          {errorsKeys.map((lot_id) => {
            const lot_id_number = Number(lot_id)
            const lotErrors = errors[lot_id_number]
            return (
              <ErrorCollapse
                errors={lotErrors}
                key={lot_id}
                lot_id={lot_id_number}
              />
            )
          })}
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

const ErrorCollapse = ({
  errors,
  lot_id,
}: {
  errors: LotError[]
  lot_id: number
}) => {
  const { t } = useTranslation()

  return (
    <Collapse
      icon={Edit}
      variant="warning"
      label={t("Lot #{{lotId}}", {
        lotId: lot_id,
      })}
      isOpen
    >
      <ul>
        {errors.map((error, index) => {
          return <li key={`${error.field}${index}`}>{getAnomalyText(error)}</li>
        })}
      </ul>
      <footer></footer>
    </Collapse>
  )
}
