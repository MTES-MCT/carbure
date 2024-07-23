import { useMemo, useState } from "react"
import { useTranslation } from "react-i18next"
import { Lot } from "../types"
import * as api from "../api"
import useEntity from "carbure/hooks/entity"
import { useMutation } from "common/hooks/async"
import { useNotify, useNotifyError } from "common/components/notifications"
import { variations } from "common/utils/formatters"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Return, Wrench } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { LotSummary } from "../components/lots/lot-summary"
import { useStatus } from "transactions/components/status"
import { TextInput } from "common/components/input"
import { useMatomo } from "matomo"
import Form from "common/components/form"

export interface RecallManyButtonProps {
  disabled?: boolean
  selection: number[]
}

export const RecallManyButton = ({
  disabled,
  selection,
}: RecallManyButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      disabled={disabled || selection.length === 0}
      variant="warning"
      icon={Wrench}
      label={t("Corriger la sélection")}
      action={() =>
        portal((close) => (
          <RecallDialog summary selection={selection} onClose={close} />
        ))
      }
    />
  )
}

export interface RecallOneButtonProps {
  icon?: boolean
  lot: Lot
}

export const RecallOneButton = ({ icon, lot }: RecallOneButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      captive
      variant={icon ? "icon" : "warning"}
      icon={Wrench}
      title={t("Corriger")}
      label={t("Corriger")}
      action={() =>
        portal((close) => <RecallDialog selection={[lot.id]} onClose={close} />)
      }
    />
  )
}

interface RecallDialogProps {
  summary?: boolean
  selection: number[]
  onClose: () => void
}

const RecallDialog = ({ summary, selection, onClose }: RecallDialogProps) => {
  const { t } = useTranslation()
  const matomo = useMatomo()
  const status = useStatus()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()

  const v = variations(selection.length)

  const [comment = "", setComment] = useState<string | undefined>("")

  const recallLots = useMutation(recallAndCommentLots, {
    invalidates: ["lots", "snapshot", "lot-details", "lot-summary"],

    onSuccess: () => {
      const text = v({
        one: t("Vous pouvez maintenant corriger le lot !"),
        many: t("Vous pouvez maintenant corriger ces lots !"),
      })

      notify(text, { variant: "success" })
      onClose()
    },

    onError: (err) => {
      const text = v({
        one: t("La demande de correction a échoué !"),
        many: t("Les demandes de correction ont échoué !"),
      })

      notifyError(err, text)
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
            one: t("Corriger le lot"),
            many: t("Corriger les lots"),
          })}
        </h1>
      </header>
      <main>
        <section>
          {v({
            one: t("Voulez-vous corriger ce lot ?"),
            many: t("Voulez-vous corriger les lots sélectionnés ?"),
          })}
        </section>
        <section>
          <Form id="recall">
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
          submit="recall"
          loading={recallLots.loading}
          variant="warning"
          icon={Wrench}
          label={t("Corriger")}
          action={() => {
            matomo.push([
              "trackEvent",
              "lot-corrections",
              "supplier-recall-lot",
              "",
              selection.length,
            ])
            recallLots.execute(entity.id, selection, comment)
          }}
        />
        <Button
          disabled={recallLots.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
        />
      </footer>
    </Dialog>
  )
}

async function recallAndCommentLots(
  entity_id: number,
  selection: number[],
  comment: string
) {
  await api.recallLots(entity_id, selection)
  await api.commentLots({ entity_id }, selection, comment)
}
