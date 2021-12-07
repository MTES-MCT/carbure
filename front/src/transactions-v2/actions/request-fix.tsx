import { useTranslation } from "react-i18next"
import { Lot } from "../types"
import * as api from "../api"
import useEntity from "carbure/hooks/entity"
import { useMutation } from "common-v2/hooks/async"
import { useNotify } from "common-v2/components/notifications"
import { variations } from "common-v2/utils/formatters"
import Button from "common-v2/components/button"
import Dialog from "common-v2/components/dialog"
import { Return, Wrench } from "common-v2/components/icons"
import { usePortal } from "common-v2/components/portal"
import { LotSummary } from "../components/lots/lot-summary"
import { useStatus } from "transactions-v2/components/status"

export interface RequestManyFixesButtonProps {
  disabled?: boolean
  selection: number[]
}

export const RequestManyFixesButton = ({
  disabled,
  selection,
}: RequestManyFixesButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      disabled={disabled || selection.length === 0}
      variant="warning"
      icon={Wrench}
      label={t("Demander des corrections")}
      action={() =>
        portal((close) => (
          <RequestFixDialog summary selection={selection} onClose={close} />
        ))
      }
    />
  )
}

export interface RequestOneFixButtonProps {
  icon?: boolean
  lot: Lot
}

export const RequestOneFixButton = ({
  icon,
  lot,
}: RequestOneFixButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      captive
      variant={icon ? "icon" : "warning"}
      icon={Wrench}
      title={t("Demander une correction")}
      label={t("Demander une correction")}
      action={() =>
        portal((close) => (
          <RequestFixDialog selection={[lot.id]} onClose={close} />
        ))
      }
    />
  )
}

interface RequestFixDialogProps {
  summary?: boolean
  selection: number[]
  onClose: () => void
}

const RequestFixDialog = ({
  summary,
  selection,
  onClose,
}: RequestFixDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const status = useStatus()
  const entity = useEntity()

  const v = variations(selection.length)

  const requestFix = useMutation(api.requestFix, {
    invalidates: ["lots", "snapshot", "lot-details"],

    onSuccess: () => {
      const text = v({
        one: t("La correction a bien été demandée !"),
        many: t("Les corrections ont bien été demandées !"),
      })

      notify(text, { variant: "success" })
      onClose()
    },

    onError: () => {
      const text = v({
        one: t("La demande de correction a échoué !"),
        many: t("Les demandes de correction ont échoué !"),
      })

      notify(text, { variant: "danger" })
      onClose()
    },
  })

  const query = { status, entity_id: entity.id }

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>
          {v({
            one: t("Demander une correction"),
            many: t("Demander des corrections"),
          })}
        </h1>
      </header>
      <main>
        <section>
          {v({
            one: t("Voulez-vous demander une correction ?"),
            many: t("Voulez-vous demander des corrections pour les lots sélectionnés ?"), // prettier-ignore
          })}
        </section>
        {summary && <LotSummary query={query} selection={selection} />}
      </main>
      <footer>
        <Button
          asideX
          disabled={requestFix.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
        />
        <Button
          submit
          loading={requestFix.loading}
          variant="warning"
          icon={Wrench}
          label={t("Demander correction")}
          action={() => requestFix.execute(entity.id, selection)}
        />
      </footer>
    </Dialog>
  )
}
