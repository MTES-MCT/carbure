import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { Lot } from "transactions/types"
import * as api from "../api"
import useEntity from "carbure/hooks/entity"
import { useMutation } from "common-v2/hooks/async"
import { useNotify } from "common-v2/components/notifications"
import { variations } from "common-v2/utils/formatters"
import Button from "common-v2/components/button"
import Dialog from "common-v2/components/dialog"
import { Pin, Return } from "common-v2/components/icons"
import { usePortal } from "common-v2/components/portal"
import { useStatus } from "transactions/components/status"
import { TextInput } from "common-v2/components/input"
import { LotSummary } from "../components/control-summary"
import Checkbox from "common-v2/components/checkbox"
import Form, { useForm } from "common-v2/components/form"

export interface PinManyButtonProps {
  disabled?: boolean
  selection: number[]
}

export const PinManyButton = ({ disabled, selection }: PinManyButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      disabled={disabled || selection.length === 0}
      variant="primary"
      icon={Pin}
      label={t("Épingler la sélection")}
      action={() =>
        portal((close) => (
          <PinDialog summary selection={selection} onClose={close} />
        ))
      }
    />
  )
}

export interface PinOneButtonProps {
  icon?: boolean
  lot: Lot
}

export const PinOneButton = ({ icon, lot }: PinOneButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      captive
      variant={icon ? "icon" : "primary"}
      icon={Pin}
      title={t("Épingler")}
      label={t("Épingler")}
      action={() =>
        portal((close) => <PinDialog selection={[lot.id]} onClose={close} />)
      }
    />
  )
}

interface PinDialogProps {
  summary?: boolean
  selection: number[]
  onClose: () => void
}

const PinDialog = ({ summary, selection, onClose }: PinDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const status = useStatus()
  const entity = useEntity()

  const v = variations(selection.length)

  const form = useForm({
    comment: undefined as string | undefined,
    notifyAuditor: false,
  })

  const pinAndComment = useMutation(pinAndCommentLots, {
    invalidates: ["control-details"],

    onSuccess: () => {
      const text = v({
        one: t("Le lot a bien été épinglé !"),
        many: t("Les lots ont bien été épinglés !"),
      })

      notify(text, { variant: "success" })
      onClose()
    },

    onError: () => {
      const text = v({
        one: t("Le lot n'a pas pu être épinglé !"),
        many: t("Les lots n'ont pas pu être épinglés !"),
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
            one: t("Épingler un lot"),
            many: t("Épingler des lots"),
          })}
        </h1>
      </header>
      <main>
        <section>
          {v({
            one: t("Voulez-vous épingler ce lot ?"),
            many: t("Voulez-vous épingler les lots sélectionnés ?"),
          })}
        </section>
        <section>
          <Form id="pin">
            <TextInput
              required
              label={t("Commentaire")}
              {...form.bind("comment")}
            />
            <Checkbox
              {...form.bind("notifyAuditor")}
              label={v({
                one: t("Signaler ce lot aux auditeurs"),
                many: t("Signaler ces lots aux auditeurs"),
              })}
            />
          </Form>
        </section>
        {summary && <LotSummary query={query} selection={selection} />}
      </main>
      <footer>
        <Button
          asideX
          disabled={pinAndComment.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
        />
        <Button
          submit="pin"
          disabled={!form.value.comment}
          loading={pinAndComment.loading}
          variant="primary"
          icon={Pin}
          label={t("Épingler")}
          action={() =>
            pinAndComment.execute(
              entity.id,
              selection,
              form.value.comment!,
              form.value.notifyAuditor
            )
          }
        />
      </footer>
    </Dialog>
  )
}

async function pinAndCommentLots(
  entity_id: number,
  selection: number[],
  comment: string,
  notifyAuditor?: boolean
) {
  await api.pinLots(entity_id, selection)
  await api.commentLots({ entity_id }, selection, comment, notifyAuditor)
}
