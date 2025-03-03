import { useTranslation } from "react-i18next"
import { Stock, StockQuery } from "../types"
import * as api from "../api"
import useEntity from "common/hooks/entity"
import { useMutation } from "common/hooks/async"
import { useNotify } from "common/components/notifications"
import { variations } from "common/utils/formatters"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Cross, Return } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { StockSummary } from "transactions/components/stocks/stock-summary"
import { useMatomo } from "matomo"

export interface CancelManyTransformButtonProps {
  query: StockQuery
  selection: number[]
}

export const CancelManyTransformButton = ({
  query,
  selection,
}: CancelManyTransformButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      disabled={selection.length === 0}
      variant="warning"
      icon={Cross}
      label={t("Annuler transformation")}
      action={() =>
        portal((close) => (
          <CancelTransformDialog
            summary
            query={query}
            selection={selection}
            onClose={close}
          />
        ))
      }
    />
  )
}

export interface CancelOneTransformButtonProps {
  icon?: boolean
  stock: Stock
}

export const CancelOneTransformButton = ({
  icon,
  stock,
}: CancelOneTransformButtonProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const portal = usePortal()

  return (
    <Button
      captive
      variant={icon ? "icon" : "warning"}
      icon={Cross}
      title={t("Annuler transformation")}
      label={t("Annuler transformation")}
      action={() =>
        portal((close) => (
          <CancelTransformDialog
            query={{ entity_id: entity.id }}
            selection={[stock.id]}
            onClose={close}
          />
        ))
      }
    />
  )
}

interface CancelTransformDialogProps {
  summary?: boolean
  query: StockQuery
  selection: number[]
  onClose: () => void
}

const CancelTransformDialog = ({
  summary,
  query,
  selection,
  onClose,
}: CancelTransformDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const matomo = useMatomo()

  const v = variations(selection.length)

  const cancelTransformations = useMutation(api.cancelTransformations, {
    invalidates: ["stocks", "snapshot", "stock-details", "stock-summary"],

    onSuccess: () => {
      const text = v({
        zero: t("Les transformations ont bien été annulées !"),
        one: t("Le transformation a bien été annulée !"),
        many: t("Les transformations sélectionnés ont bien été annulées !"),
      })

      notify(text, { variant: "success" })
      onClose()
    },

    onError: () => {
      const text = v({
        zero: t("Les transformations n'ont pas pu être annulées !"),
        one: t("Le transformation n'a pas pu être annulée !"),
        many: t("Les transformations sélectionnés n'ont pas pu être annulées !"), // prettier-ignore
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
            one: t("Annuler la transformation"),
            many: t("Annuler les transformations sélectionnés"),
          })}
        </h1>
      </header>
      <main>
        <section>
          {v({
            one: t("Voulez-vous annuler cette transformation ?"),
            many: t("Voulez-vous annuler les transformations sélectionnées ?"),
          })}
        </section>
        {summary && <StockSummary query={query} selection={selection} />}
      </main>
      <footer>
        <Button
          asideX
          autoFocus
          loading={cancelTransformations.loading}
          variant="warning"
          icon={Cross}
          label={t("Annuler transformation")}
          action={() => {
            matomo.push([
              "trackEvent",
              "stocks",
              "cancel-transform",
              selection.length,
            ])
            cancelTransformations.execute(query.entity_id, selection)
          }}
        />
        <Button
          disabled={cancelTransformations.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
        />
      </footer>
    </Dialog>
  )
}
