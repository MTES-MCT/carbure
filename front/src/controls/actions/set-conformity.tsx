import { useMemo, useState } from "react"
import { useTranslation } from "react-i18next"
import { Lot } from "transactions/types"
import * as api from "../api/auditor"
import useEntity from "common/hooks/entity"
import { useMutation } from "common/hooks/async"
import { useNotify } from "common/components/notifications"
import { variations } from "common/utils/formatters"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Check, Cross, Return } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { useStatus } from "../components/status"
import { ControlLotSummary } from "../components/lots/control-lot-summary"
import Form from "common/components/form"
import { TextInput } from "common/components/input"
import i18next from "i18next"

export interface SetManyConformityButtonProps {
  disabled?: boolean
  selection: number[]
}

export const SetManyConformityButton = ({
  disabled,
  selection,
}: SetManyConformityButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      disabled={disabled || selection.length === 0}
      variant="primary"
      icon={Check}
      label={t("Définir la conformité")}
      action={() =>
        portal((close) => (
          <ConformityDialog summary selection={selection} onClose={close} />
        ))
      }
    />
  )
}

export interface SetOneConformityButtonProps {
  icon?: boolean
  lot: Lot
}

export const SetOneConformityButton = ({
  icon,
  lot,
}: SetOneConformityButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      captive
      variant={icon ? "icon" : "primary"}
      icon={Check}
      title={t("Définir la conformité")}
      label={t("Définir la conformité")}
      action={() =>
        portal((close) => (
          <ConformityDialog selection={[lot.id]} onClose={close} />
        ))
      }
    />
  )
}

interface ConformityDialogProps {
  summary?: boolean
  selection: number[]
  onClose: () => void
}

const ConformityDialog = ({
  summary,
  selection,
  onClose,
}: ConformityDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const status = useStatus()
  const entity = useEntity()

  const v = variations(selection.length)

  const [comment, setComment] = useState<string | undefined>(undefined)

  const markAsConform = useMutation(markAsConformAndComment, {
    invalidates: ["controls", "control-details", "controls-snapshot"],

    onSuccess: () => {
      const text = v({
        one: t("Le lot a bien été marqué comme conforme !"),
        many: t("Les lots ont bien été marqués comme conformes !"),
      })

      notify(text, { variant: "success" })
      onClose()
    },

    onError: () => {
      const text = v({
        one: t("Le lot n'a pas pu être marqué comme conforme !"),
        many: t("Les lots n'ont pas pu être marqué comme conforme !"),
      })

      notify(text, { variant: "danger" })
      onClose()
    },
  })

  const markAsNonConform = useMutation(markAsNonConformAndComment, {
    invalidates: ["controls", "control-details", "controls-snapshot"],

    onSuccess: () => {
      const text = v({
        one: t("Le lot a bien été marqué comme non conforme !"),
        many: t("Les lots ont bien été marqués comme non conformes !"),
      })

      notify(text, { variant: "success" })
      onClose()
    },

    onError: () => {
      const text = v({
        one: t("Le lot n'a pas pu être marqué comme non conforme !"),
        many: t("Les lots n'ont pas pu être marqué comme non conforme !"),
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
            one: t("Définir la conformité d'un lot"),
            many: t("Définir la conformité des lots"),
          })}
        </h1>
      </header>
      <main>
        <section>
          <p>
            {t(
              "Veuillez définir le niveau de conformité des lots sélectionnés en cliquant sur l'un des boutons au bas de cette fenêtre."
            )}
          </p>
        </section>
        <section>
          <Form id="conformity-form">
            <TextInput
              autoFocus
              required
              label={t("Commentaire")}
              value={comment}
              onChange={setComment}
            />
          </Form>
        </section>

        {summary && <ControlLotSummary query={query} selection={selection} />}
      </main>
      <footer>
        <Button
          asideX
          disabled={markAsNonConform.loading}
          loading={markAsConform.loading}
          variant="success"
          icon={Check}
          label={t("CONFORME")}
          action={() => markAsConform.execute(entity.id, selection, comment!)}
        />
        <Button
          disabled={markAsConform.loading}
          loading={markAsNonConform.loading}
          variant="danger"
          icon={Cross}
          label={t("NON CONFORME")}
          action={() =>
            markAsNonConform.execute(entity.id, selection, comment!)
          }
        />
        <Button
          disabled={markAsConform.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
        />
      </footer>
    </Dialog>
  )
}

async function markAsConformAndComment(
  entity_id: number,
  selection: number[],
  comment: string
) {
  const fullComment = `[${i18next.t("CONFORME")}] ${comment}`
  await api.markAsConform(entity_id, selection)
  await api.commentLots({ entity_id }, selection, fullComment, true, true)
}

async function markAsNonConformAndComment(
  entity_id: number,
  selection: number[],
  comment: string
) {
  const fullComment = `[${i18next.t("NON CONFORME")}] ${comment}`
  await api.markAsNonConform(entity_id, selection)
  await api.commentLots({ entity_id }, selection, fullComment, true, true)
}
