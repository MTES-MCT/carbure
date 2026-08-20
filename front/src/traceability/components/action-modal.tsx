import { useLocation, useNavigate } from "react-router-dom"
import { useTranslation } from "react-i18next"

import Dialog from "common/components/dialog2/dialog"
import { useHashMatch } from "common/components/hash-route"
import Portal from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"

import { getActionDetail } from "traceability/api"
import { ActionField } from "traceability/hooks/use-action-fields"
import { ActionForm } from "traceability/components/action-form"

export type ActionModalProps = {
  fields?: ActionField[]
}

export const ActionModal = ({ fields }: ActionModalProps) => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const entity = useEntity()
  const match = useHashMatch("action/:id")

  const actionResponse = useQuery(getActionDetail, {
    key: "traceability-action-detail",
    params: [entity.id, parseInt(match?.params.id ?? "", 10)],
  })

  const action = actionResponse.result?.data

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog
        size="large"
        onClose={closeDialog}
        header={
          <Dialog.Title>
            {t("Action n°")}
            {action?.id ?? "..."}
          </Dialog.Title>
        }
      >
        <ActionForm action={action} fields={fields} />

        {actionResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}

export default ActionModal
