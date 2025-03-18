import { useTranslation } from "react-i18next"
import { Stock } from "../types"
import * as api from "../api"
import useEntity from "common/hooks/entity"
import { useMutation } from "common/hooks/async"
import { usePortal } from "common/components/portal"
import { useNotify } from "common/components/notifications"
import { variations } from "common/utils/formatters"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { DropOff, Return } from "common/components/icons"
import { useMatomo } from "matomo"
import { StockSummary } from "transactions/components/stocks/stock-summary"
import { useMemo, useState } from "react"
import { TextInput } from "common/components/input"
import Form from "common/components/form"

export interface FlushManyButtonProps {
  disabled?: boolean
  selection: number[]
}

export const FlushManyButton = ({
  disabled,
  selection,
}: FlushManyButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      disabled={disabled || selection.length === 0}
      variant="danger"
      icon={DropOff}
      label={t("Marquer comme vide")}
      action={() =>
        portal((close) => (
          <FlushDialog summary selection={selection} onClose={close} />
        ))
      }
    />
  )
}

export interface FlushOneButtonProps {
  icon?: boolean
  stock: Stock
}

export const FlushOneButton = ({ icon, stock }: FlushOneButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      captive
      variant={icon ? "icon" : "danger"}
      icon={DropOff}
      label={t("Marquer comme vide")}
      action={() =>
        portal((close) => (
          <FlushDialog selection={[stock.id]} onClose={close} />
        ))
      }
    />
  )
}

interface FlushDialogProps {
  summary?: boolean
  selection: number[]
  onClose: () => void
}

const FlushDialog = ({ summary, selection, onClose }: FlushDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const matomo = useMatomo()
  const entity = useEntity()

  const v = variations(selection.length)

  const [freeField, setFreeField] = useState<string | undefined>("")

  const query = useMemo(() => ({ entity_id: entity.id }), [entity.id])

  const flushStocks = useMutation(api.flushStocks, {
    invalidates: ["stocks", "snapshot", "stock-details", "stock-summary"],

    onSuccess: () => {
      const text = v({
        zero: t("Les stocks ont bien été vidés !"),
        one: t("Le stock a bien été vidé !"),
        many: t("Les stocks sélectionnés ont bien été vidés !"),
      })

      notify(text, { variant: "success" })
      onClose()
    },

    onError: () => {
      const text = v({
        zero: t("Les stocks n'ont pas pu être vidés !"),
        one: t("Le stock n'a pas pu être vidé !"),
        many: t("Les stocks sélectionnés n'ont pas pu être vidés !"),
      })

      notify(text, { variant: "danger" })
      onClose()
    },
  })

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>
          {v({
            zero: t("Vider tous les stocks"),
            one: t("Vider ce stock"),
            many: t("Vider les stocks sélectionnés"),
          })}
        </h1>
      </header>
      <main>
        <section>
          {t(
            "Les stocks sélectionnés seront vidés de leur volume restant et ne pourront plus être utilisés, êtes vous sûr de vouloir continuer ?"
          )}
        </section>
        <section>
          <Form
            id="flush-form"
            onSubmit={() => {
              matomo.push([
                "trackEvent",
                "stock",
                "flush-stock",
                "",
                selection.length,
              ])
              flushStocks.execute(entity.id, selection, freeField!)
            }}
          >
            <TextInput
              autoFocus
              label={t("Commentaire (optionnel)")}
              value={freeField}
              onChange={setFreeField}
            />
          </Form>
        </section>
        {summary && <StockSummary query={query} selection={selection} />}
      </main>
      <footer>
        <Button
          asideX
          submit="flush-form"
          loading={flushStocks.loading}
          variant="danger"
          icon={DropOff}
          label={t("Vider")}
        />
        <Button
          disabled={flushStocks.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
        />
      </footer>
    </Dialog>
  )
}
