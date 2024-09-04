import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Lot, LotQuery } from "../types"
import * as api from "../api"
import useEntity from "carbure/hooks/entity"
import { useMutation } from "common/hooks/async"
import { usePortal } from "common/components/portal"
import { useNotify } from "common/components/notifications"
import { variations } from "common/utils/formatters"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Cross, Return } from "common/components/icons"
import { TextInput } from "common/components/input"
import { LotSummary } from "../components/lots/lot-summary"
import Form from "common/components/form"

export interface RejectManyButtonProps {
  disabled?: boolean
  query: LotQuery
  selection: number[]
}

export const RejectManyButton = ({
  disabled,
  query,
  selection,
}: RejectManyButtonProps) => {
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

export interface RejectOneButtonProps {
  icon?: boolean
  lot: Lot
}

export const RejectOneButton = ({ icon, lot }: RejectOneButtonProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const portal = usePortal()

  return (
    <Button
      captive
      variant={icon ? "icon" : "danger"}
      icon={Cross}
      title={t("Refuser")}
      label={t("Refuser")}
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

  const [comment = "", setComment] = useState<string | undefined>("")

  const rejectLots = useMutation(rejectAndCommentLots, {
    invalidates: ["lots", "snapshot", "lot-details", "lot-summary"],

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
        <section>
          <Form
            id="reject"
            onSubmit={() => {
              // matomo.push([
              //   "trackEvent",
              //   "lot-corrections",
              //   "client-reject-lot",
              //   "",
              //   selection.length,
              // ])
              rejectLots.execute(query, selection, comment)
            }}
          >
            <TextInput
              autoFocus
              required
              label={t("Commentaire")}
              value={comment}
              onChange={setComment}
            />
          </Form>
        </section>
        {summary && <LotSummary query={query} selection={selection} />}
      </main>
      <footer>
        <Button
          asideX
          submit="reject"
          loading={rejectLots.loading}
          disabled={comment.length === 0}
          variant="danger"
          icon={Cross}
          label={t("Refuser")}
        />
        <Button
          disabled={rejectLots.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
        />
      </footer>
    </Dialog>
  )
}

async function rejectAndCommentLots(
  query: LotQuery,
  selection: number[] | undefined,
  comment: string
) {
  await api.rejectLots(query, selection)
  await api.commentLots(query, selection, comment)
}
