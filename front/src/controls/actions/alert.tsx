import useEntity, { EntityManager } from "carbure/hooks/entity"
import Button from "common/components/button"
import Checkbox from "common/components/checkbox"
import Dialog from "common/components/dialog"
import Form, { useForm } from "common/components/form"
import {
  AlertTriangle,
  AlertTriangleOff,
  Return,
} from "common/components/icons"
import { TextInput } from "common/components/input"
import { useNotify } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { variations } from "common/utils/formatters"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { Lot } from "transactions/types"
import pickApi from "../api"
import { ControlLotSummary } from "../components/lots/control-lot-summary"
import { useStatus } from "../components/status"

export interface AlertManyButtonProps {
  disabled?: boolean
  pinned?: boolean
  selection: number[]
  lots: Lot[]
}

export const AlertManyButton = ({
  disabled,
  selection,
  pinned: forcePinned,
  lots,
}: AlertManyButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()
  const entity = useEntity()

  const pinned =
    forcePinned ||
    (lots.length > 0 && lots.every((lot) => isPinned(entity, lot)))

  return (
    <Button
      disabled={disabled || selection.length === 0}
      variant="warning"
      icon={pinned ? AlertTriangleOff : AlertTriangle}
      label={pinned ? t("Annuler le signalement") : t("Signaler la sélection")} // prettier-ignore
      action={() =>
        portal((close) => (
          <AlertDialog
            summary
            pinned={pinned}
            selection={selection}
            onClose={close}
          />
        ))
      }
    />
  )
}

export interface AlertOneButtonProps {
  icon?: boolean
  lot: Lot
}

export const AlertOneButton = ({ icon, lot }: AlertOneButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  const entity = useEntity()
  const pinned = isPinned(entity, lot)

  return (
    <Button
      captive
      variant={icon ? "icon" : "warning"}
      icon={pinned ? AlertTriangleOff : AlertTriangle}
      title={pinned ? t("Annuler le signalement") : t("Signaler")}
      label={pinned ? t("Annuler le signalement") : t("Signaler")}
      action={() =>
        portal((close) => (
          <AlertDialog pinned={pinned} selection={[lot.id]} onClose={close} />
        ))
      }
    />
  )
}

interface AlertDialogProps {
  pinned?: boolean
  summary?: boolean
  selection: number[]
  onClose: () => void
}

const AlertDialog = ({
  pinned,
  summary,
  selection,
  onClose,
}: AlertDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const status = useStatus()
  const entity = useEntity()

  const v = variations(selection.length)

  const form = useForm({
    comment: undefined as string | undefined,
    notifyExternal: false,
  })

  const pinAndComment = useMutation(pinAndCommentLots, {
    invalidates: ["controls", "control-details", "controls-snapshot"],

    onSuccess: () => {
      const text = v({
        one: t("Le lot a bien été mis à jour !"),
        many: t("Les lots ont bien été mis à jour !"),
      })

      notify(text, { variant: "success" })
      onClose()
    },

    onError: () => {
      const text = v({
        one: t("Le lot n'a pas pu être mis à jour !"),
        many: t("Les lots n'ont pas pu être mis à jour !"),
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
            one: pinned ? t("Annuler un signalement") : t("Signaler un lot"),
            many: pinned
              ? t("Annuler des signalements")
              : t("Signaler des lots"),
          })}
        </h1>
      </header>
      <main>
        <section>
          <p>
            {v({
              one: pinned
                ? t("Voulez-vous annuler le signalement de ce lot ?")
                : t("Voulez-vous signaler ce lot ?"),
              many: pinned
                ? t("Voulez-vous annuler le signalement des lots sélectionnés ?") // prettier-ignore
                : t("Voulez-vous signaler les lots sélectionnés ?"),
            })}
          </p>
          {!pinned && selection.length > 1 && (
            <p>
              {v({
                one: "",
                many: t("Si des lots déjà signalés sont sélectionnés, leur signalement sera annulé."), // prettier-ignore
              })}
            </p>
          )}
        </section>
        {!pinned && (
          <section>
            <Form id="pin">
              <TextInput
                autoFocus
                label={t("Commentaire (optionnel)")}
                {...form.bind("comment")}
              />
              <Checkbox
                {...form.bind("notifyExternal")}
                label={v({
                  one: entity.isAdmin
                    ? t("Signaler ce lot aux auditeurs")
                    : t("Signaler ce lot à l'administration"),
                  many: entity.isAdmin
                    ? t("Signaler ces lots aux auditeurs")
                    : t("Signaler ces lots à l'administration"),
                })}
              />
            </Form>
          </section>
        )}
        {summary && <ControlLotSummary query={query} selection={selection} />}
      </main>
      <footer>
        <Button
          asideX
          submit="pin"
          loading={pinAndComment.loading}
          variant="warning"
          icon={pinned ? AlertTriangleOff : AlertTriangle}
          label={pinned ? t("Annuler le signalement") : t("Signaler")}
          action={() =>
            pinAndComment.execute(
              entity,
              selection,
              form.value.comment,
              form.value.notifyExternal
            )
          }
        />
        <Button
          disabled={pinAndComment.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
        />
      </footer>
    </Dialog>
  )
}

async function pinAndCommentLots(
  entity: EntityManager,
  selection: number[],
  comment?: string,
  notifyExternal = false
) {
  const notifyAdmin = entity.isAdmin || (entity.isAuditor && notifyExternal)
  const notifyAuditor = entity.isAuditor || (entity.isAdmin && notifyExternal)

  const api = pickApi(entity)
  await api.pinLots(entity.id, selection, notifyAdmin, notifyAuditor)

  if (comment !== undefined) {
    await api.commentLots(
      { entity_id: entity.id },
      selection,
      comment,
      notifyAdmin,
      notifyAuditor
    )
  }
}

function isPinned(entity: EntityManager, lot: Lot) {
  if (entity.isAdmin) return lot.highlighted_by_admin === true
  if (entity.isAuditor) return lot.highlighted_by_auditor === true
  else return false
}
