import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { useQuery } from "common/hooks/async"
import { useNavigate } from "react-router-dom"
import * as api from "./api"
import useEntity from "carbure/hooks/entity"
import { useHashMatch } from "common/components/hash-route"
import { formatOperationType } from "material-accounting/operations/operations.utils"

export const OperationDetail = () => {
  const navigate = useNavigate()
  const entity = useEntity()
  const match = useHashMatch("operation/:id")

  const { result } = useQuery(api.getOperationDetail, {
    key: "operation-detail",
    params: [entity.id, parseInt(match?.params.id ?? "")],
  })

  const operation = result?.data

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog fullscreen onClose={closeDialog}>
        {operation && (
          <>
            <Dialog.Title>
              {formatOperationType(operation.type)} n°{operation.id}
            </Dialog.Title>
            <Dialog.Description>descr</Dialog.Description>
          </>
        )}
      </Dialog>
    </Portal>
  )
}
