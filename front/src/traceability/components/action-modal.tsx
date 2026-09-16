import { useLocation, useNavigate } from "react-router-dom"

import Dialog from "common/components/dialog2/dialog"
import { Button } from "common/components/button2"
import { useHashMatch } from "common/components/hash-route"
import Portal from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"

import { getActionDetail } from "traceability/api"
import type { DetailAction } from "traceability/components/actions-page"
import { ActionForm } from "traceability/components/action-form"
import { ActionFieldset } from "traceability/hooks/action-fields"
import { ActionIndustry } from "traceability/types"

export type ActionModalProps = {
  title: string
  fieldsets: ActionFieldset[]
  industry: ActionIndustry
  detailActions?: DetailAction[]
}

export const ActionModal = ({
  title,
  fieldsets,
  industry,
  detailActions,
}: ActionModalProps) => {
  const navigate = useNavigate()
  const location = useLocation()
  const entity = useEntity()
  const match = useHashMatch("action/:id")

  const actionResponse = useQuery(getActionDetail, {
    key: "traceability-action-detail",
    params: [entity.id, parseInt(match?.params.id ?? "", 10), industry],
  })

  const action = actionResponse.result?.data

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog
        onClose={closeDialog}
        header={
          <Dialog.Title>
            {title}
            {action?.id ?? "..."}
          </Dialog.Title>
        }
        footer={
          detailActions && detailActions.length > 0 && action ? (
            <>
              {detailActions.map((detailAction) => (
                <Button
                  key={detailAction.label}
                  iconId={detailAction.icon}
                  priority={detailAction.priority}
                  customPriority={detailAction.variant}
                  onClick={() => detailAction.onAction(action)}
                >
                  {detailAction.label}
                </Button>
              ))}
            </>
          ) : undefined
        }
      >
        <ActionForm action={action} fieldsets={fieldsets} />

        {actionResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}

export default ActionModal
