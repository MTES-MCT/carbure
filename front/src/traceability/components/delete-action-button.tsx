import { useLocation, useNavigate } from "react-router-dom"
import { useTranslation } from "react-i18next"

import { Button } from "common/components/button2"
import { Confirm } from "common/components/dialog2"
import { useNotify, useNotifyError } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import { useMutation } from "common/hooks/async"
import useEntity from "common/hooks/entity"

import { deleteAction } from "traceability/api"
import { QUERY_KEY } from "traceability/components/actions-page"
import { Action, ActionStatus, ActionType } from "traceability/types"

const DELETABLE_STATUSES: Set<ActionStatus> = new Set([
  ActionStatus.PENDING,
  ActionStatus.REJECTED,
])

export function canDeleteAction(action: Action, canWrite: boolean) {
  return (
    canWrite &&
    action.type === ActionType.INIT &&
    action.status != null &&
    DELETABLE_STATUSES.has(action.status)
  )
}

type DeleteActionButtonProps = {
  action: Action
}

export const DeleteActionButton = ({ action }: DeleteActionButtonProps) => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const entity = useEntity()
  const portal = usePortal()
  const notify = useNotify()
  const notifyError = useNotifyError()

  const deletion = useMutation(deleteAction, {
    invalidates: [QUERY_KEY],
    onSuccess: () => {
      notify(t("Le lot a bien été supprimé."), { variant: "success" })
      navigate({ search: location.search, hash: "#" })
    },
    onError: (err) => {
      notifyError(err)
    },
  })

  if (!canDeleteAction(action, entity.canWrite())) return null

  return (
    <Button
      iconId="fr-icon-close-line"
      customPriority="danger"
      onClick={() =>
        portal((close) => (
          <Confirm
            title={t("Supprimer le lot")}
            description={t("Voulez-vous supprimer le lot {{id}} ?", {
              id: action.id,
            })}
            confirm={t("Supprimer")}
            icon="fr-icon-close-line"
            customVariant="danger"
            hideCancel
            onConfirm={() =>
              deletion.execute(entity.id, action.id, action.industry)
            }
            onClose={close}
          />
        ))
      }
    >
      {t("Supprimer")}
    </Button>
  )
}
