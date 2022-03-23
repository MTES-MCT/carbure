import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { Lot } from "transactions/types"
import pickApi from "../api"
import useEntity, { EntityManager } from "carbure/hooks/entity"
import { useMutation } from "common-v2/hooks/async"
import { useNotify } from "common-v2/components/notifications"
import { variations } from "common-v2/utils/formatters"
import Button from "common-v2/components/button"
import Dialog from "common-v2/components/dialog"
import { Pin, PinOff, Return } from "common-v2/components/icons"
import { usePortal } from "common-v2/components/portal"
import { useStatus } from "../components/status"
import { TextInput } from "common-v2/components/input"
import { LotSummary } from "../components/lots/control-lot-summary"
import Checkbox from "common-v2/components/checkbox"
import Form, { useForm } from "common-v2/components/form"
import { AdminStatus } from "controls/types"

export interface PinManyButtonProps {
  disabled?: boolean
  pinned?: boolean
  selection: number[]
  lots: Lot[]
}

export const PinManyButton = ({
  disabled,
  selection,
  pinned: forcePinned,
  lots,
}: PinManyButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()
  const entity = useEntity()
  const status = useStatus() as AdminStatus

  const pinned =
    forcePinned ||
    status === "pinned" ||
    (lots.length > 0 && lots.every((lot) => isPinned(entity, lot)))

  return (
    <Button
      disabled={disabled || selection.length === 0}
      variant={pinned ? "warning" : "primary"}
      icon={pinned ? PinOff : Pin}
      label={pinned ? t("Désépingler la sélection") : t("Épingler la sélection")} // prettier-ignore
      action={() =>
        portal((close) => (
          <PinDialog
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

export interface PinOneButtonProps {
  icon?: boolean
  lot: Lot
}

export const PinOneButton = ({ icon, lot }: PinOneButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  const entity = useEntity()
  const pinned = isPinned(entity, lot)

  return (
    <Button
      captive
      variant={icon ? "icon" : pinned ? "warning" : "primary"}
      icon={pinned ? PinOff : Pin}
      title={pinned ? t("Désépingler") : t("Épingler")}
      label={pinned ? t("Désépingler") : t("Épingler")}
      action={() =>
        portal((close) => (
          <PinDialog pinned={pinned} selection={[lot.id]} onClose={close} />
        ))
      }
    />
  )
}

interface PinDialogProps {
  pinned?: boolean
  summary?: boolean
  selection: number[]
  onClose: () => void
}

const PinDialog = ({ pinned, summary, selection, onClose }: PinDialogProps) => {
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
            one: pinned ? t("Désépingler un lot") : t("Épingler un lot"),
            many: pinned ? t("Désépingler des lots") : t("Épingler des lots"),
          })}
        </h1>
      </header>
      <main>
        <section>
          <p>
            {v({
              one: pinned
                ? t("Voulez-vous désépingler ce lot ?")
                : t("Voulez-vous épingler ce lot ?"),
              many: pinned
                ? t("Voulez-vous désépingler les lots sélectionnés ?")
                : t("Voulez-vous épingler les lots sélectionnés ?"),
            })}{" "}
          </p>
          {!pinned && selection.length > 1 && (
            <p>
              {v({
                one: "",
                many: t("Si des lots déjà épinglés sont sélectionnés, ils seront désépinglés."), // prettier-ignore
              })}
            </p>
          )}
        </section>
        {!pinned && (
          <section>
            <Form id="pin">
              <TextInput
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
        {summary && <LotSummary query={query} selection={selection} />}
      </main>
      <footer>
        <Button
          asideX
          submit="pin"
          loading={pinAndComment.loading}
          variant={pinned ? "warning" : "primary"}
          icon={Pin}
          label={pinned ? t("Désépingler") : t("Épingler")}
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
  notifyExternal: boolean = false
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
