import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { Lot } from "../types"
import * as api from "../api"
import useEntity from "common/hooks/entity"
import { useMutation } from "common/hooks/async"
import { useNotify } from "common/components/notifications"
import { variations } from "common/utils/formatters"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Check, Return } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { useStatus } from "transactions/components/status"
import { LotSummary } from "../components/lots/lot-summary"
import { useMatomo } from "matomo"

export interface ApproveManyFixesButtonProps {
  disabled?: boolean
  selection: number[]
}

export const ApproveManyFixesButton = ({
  disabled,
  selection,
}: ApproveManyFixesButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      disabled={disabled || selection.length === 0}
      variant="success"
      icon={Check}
      label={t("Accepter les corrections")}
      action={() =>
        portal((close) => (
          <ApproveFixDialog summary selection={selection} onClose={close} />
        ))
      }
    />
  )
}

export interface ApproveOneFixButtonProps {
  icon?: boolean
  lot: Lot
}

export const ApproveOneFixButton = ({
  icon,
  lot,
}: ApproveOneFixButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      captive
      variant={icon ? "icon" : "success"}
      icon={Check}
      title={t("Accepter la correction")}
      label={t("Accepter la correction")}
      action={() =>
        portal((close) => (
          <ApproveFixDialog selection={[lot.id]} onClose={close} />
        ))
      }
    />
  )
}

interface ApproveFixDialogProps {
  summary?: boolean
  selection: number[]
  onClose: () => void
}

const ApproveFixDialog = ({
  summary,
  selection,
  onClose,
}: ApproveFixDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const matomo = useMatomo()
  const status = useStatus()
  const entity = useEntity()

  const v = variations(selection.length)

  const approveFix = useMutation(api.approveFix, {
    invalidates: [
      "lots",
      "snapshot",
      "lot-details",
      "lot-summary",
      `nav-stats-${entity.id}`,
    ],

    onSuccess: () => {
      const text = v({
        one: t("La correction a bien été accepté !"),
        many: t("Les corrections ont bien été acceptés !"),
      })

      notify(text, { variant: "success" })
      onClose()
    },

    onError: () => {
      const text = v({
        one: t("La correction n'a pas pu être acceptée !"),
        many: t("Les corrections n'ont pas pu être acceptée !"),
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
            one: t("Accepter la correction"),
            many: t("Accepter les corrections"),
          })}
        </h1>
      </header>
      <main>
        <section>
          {v({
            one: t("Voulez-vous accepter cette correction ?"),
            many: t("Voulez-vous accepter les corrections des lots sélectionnés ?"), // prettier-ignore
          })}
        </section>
        {summary && <LotSummary query={query} selection={selection} />}
      </main>
      <footer>
        <Button
          asideX
          autoFocus
          loading={approveFix.loading}
          variant="primary"
          icon={Check}
          label={t("Accepter correction")}
          action={() => {
            matomo.push([
              "trackEvent",
              "lot-corrections",
              "client-approve-fix",
              "",
              selection.length,
            ])
            approveFix.execute(entity.id, selection)
          }}
        />
        <Button
          disabled={approveFix.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
        />
      </footer>
    </Dialog>
  )
}
