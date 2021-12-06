import { useTranslation } from "react-i18next"
import { Lot, LotQuery } from "../types"
import * as api from "../api"
import useEntity from "carbure/hooks/entity"
import { useMutation } from "common-v2/hooks/async"
import { useNotify } from "common-v2/components/notifications"
import { variations } from "common-v2/utils/formatters"
import Button from "common-v2/components/button"
import Dialog from "common-v2/components/dialog"
import { Cross, Return } from "common-v2/components/icons"
import { usePortal } from "common-v2/components/portal"
import { LotSummary } from "../components/lots/lot-summary"

export interface RejectButtonProps {
  disabled?: boolean
  query: LotQuery
  selection: number[]
}

export const RejectManyButton = ({
  disabled,
  query,
  selection,
}: RejectButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      disabled={disabled}
      variant="danger"
      icon={Cross}
      label={
        selection.length > 0 ? t("Refuser la sélection") : t("Refuser tout")
      }
      action={() =>
        portal((close) => (
          <RejectDialog
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

export interface RejectIconButtonProps {
  icon?: boolean
  lot: Lot
}

export const RejectOneButton = ({ icon, lot }: RejectIconButtonProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const portal = usePortal()

  return (
    <Button
      captive
      variant={icon ? "icon" : "danger"}
      icon={Cross}
      title={t("Refuser le lot")}
      label={t("Refuser le lot")}
      action={() =>
        portal((close) => (
          <RejectDialog
            query={{ entity_id: entity.id }}
            selection={[lot.id]}
            onClose={close}
          />
        ))
      }
    />
  )
}

interface RejectDialogProps {
  summary?: boolean
  query: LotQuery
  selection: number[]
  onClose: () => void
}

const RejectDialog = ({
  summary,
  query,
  selection,
  onClose,
}: RejectDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()

  const v = variations(selection.length)

  const rejectLots = useMutation(api.rejectLots, {
    invalidates: ["lots", "snapshot", "lot-details"],

    onSuccess: () => {
      const text = v({
        zero: t("Les lots ont bien été refusés !"),
        one: t("Le lot a bien été refusé !"),
        many: t("Les lots sélectionnés ont bien été refusés !"),
      })

      notify(text, { variant: "success" })
      onClose()
    },

    onError: () => {
      const text = v({
        zero: t("Les lots n'ont pas pu être refusés !"),
        one: t("Le lot n'a pas pu être refusé !"),
        many: t("Les lots sélectionnés n'ont pas pu être refusés !"),
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
            zero: t("Refuser tous les lots"),
            one: t("Refuser ce lot"),
            many: t("Refuser les lots sélectionnés"),
          })}
        </h1>
      </header>
      <main>
        <section>
          {v({
            zero: t("Voulez-vous refuser ces lots ?"),
            one: t("Voulez-vous refuser ce lot ?"),
            many: t("Voulez-vous refuser les lots sélectionnés ?"),
          })}
        </section>
        {summary && <LotSummary query={query} selection={selection} />}
      </main>
      <footer>
        <Button
          asideX
          disabled={rejectLots.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
        />
        <Button
          submit
          loading={rejectLots.loading}
          variant="danger"
          icon={Cross}
          label={t("Refuser")}
          action={() => rejectLots.execute(query, selection)}
        />
      </footer>
    </Dialog>
  )
}
