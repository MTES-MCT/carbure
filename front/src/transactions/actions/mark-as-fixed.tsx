import { useMemo, useState } from "react"
import { useTranslation } from "react-i18next"
import { Lot } from "../types"
import * as api from "../api"
import useEntity from "carbure/hooks/entity"
import { useMutation } from "common-v2/hooks/async"
import { useNotify } from "common-v2/components/notifications"
import { variations } from "common-v2/utils/formatters"
import Button from "common-v2/components/button"
import Dialog from "common-v2/components/dialog"
import { Check, Return } from "common-v2/components/icons"
import { usePortal } from "common-v2/components/portal"
import { TextInput } from "common-v2/components/input"
import { useStatus } from "transactions/components/status"
import { LotSummary } from "../components/lots/lot-summary"

export interface MarkManyAsFixedButtonProps {
  disabled?: boolean
  selection: number[]
}

export const MarkManyAsFixedButton = ({
  disabled,
  selection,
}: MarkManyAsFixedButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      disabled={disabled || selection.length === 0}
      variant="success"
      icon={Check}
      label={t("Valider les corrections")}
      action={() =>
        portal((close) => (
          <MarkAsFixedDialog summary selection={selection} onClose={close} />
        ))
      }
    />
  )
}

export interface MarkOneAsFixedButtonProps {
  icon?: boolean
  lot: Lot
}

export const MarkOneAsFixedButton = ({
  icon,
  lot,
}: MarkOneAsFixedButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      captive
      variant={icon ? "icon" : "success"}
      icon={Check}
      title={t("Valider la correction")}
      label={t("Valider la correction")}
      action={() =>
        portal((close) => (
          <MarkAsFixedDialog selection={[lot.id]} onClose={close} />
        ))
      }
    />
  )
}

interface MarkAsFixedDialogProps {
  summary?: boolean
  selection: number[]
  onClose: () => void
}

const MarkAsFixedDialog = ({
  summary,
  selection,
  onClose,
}: MarkAsFixedDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const status = useStatus()
  const entity = useEntity()

  const v = variations(selection.length)

  const [comment = "", setComment] = useState<string | undefined>("")

  const markAsFixed = useMutation(markAsFixedAndCommentLots, {
    invalidates: ["lots", "snapshot", "lot-details", "lot-summary"],

    onSuccess: () => {
      const text = v({
        one: t("La correction a bien été validée !"),
        many: t("Les corrections ont bien été validées !"),
      })

      notify(text, { variant: "success" })
      onClose()
    },

    onError: () => {
      const text = v({
        one: t("La validation de la correction a échoué !"),
        many: t("Les validations des corrections ont échoué !"),
      })

      notify(text, { variant: "danger" })
      onClose()
    },
  })

  const query = useMemo(
    () => ({ status, entity_id: entity.id }),
    [status, entity.id]
  )

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>
          {v({
            one: t("Valider la correction"),
            many: t("Valider les corrections"),
          })}
        </h1>
      </header>
      <main>
        <section>
          {v({
            one: t("Voulez-vous valider cette correction ?"),
            many: t("Voulez-vous valider les corrections des lots sélectionnés ?"), // prettier-ignore
          })}
        </section>
        <section>
          <TextInput
            required
            label={t("Commentaire")}
            value={comment}
            onChange={setComment}
          />
        </section>
        {summary && <LotSummary query={query} selection={selection} />}
      </main>
      <footer>
        <Button
          asideX
          disabled={markAsFixed.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
        />
        <Button
          submit
          loading={markAsFixed.loading}
          variant="success"
          icon={Check}
          label={t("Valider correction")}
          action={() =>
            markAsFixed.execute(entity.id, selection, status, comment)
          }
        />
      </footer>
    </Dialog>
  )
}

async function markAsFixedAndCommentLots(
  entity_id: number,
  selection: number[],
  status: string,
  comment: string
) {
  await api.markAsFixed(entity_id, selection)
  await api.commentLots({ entity_id, status }, selection, comment)
}
