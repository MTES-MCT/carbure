import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { useQuery } from "common/hooks/async"
import { useNavigate } from "react-router-dom"
import * as api from "accounting/api/biofuels/operations"
import useEntity from "common/hooks/entity"
import { useHashMatch } from "common/components/hash-route"
import { OperationBadge } from "accounting/components/operation-badge/operation-badge"
import css from "../../../operations.module.css"
import { Text } from "common/components/text"
import { Grid, LoaderOverlay, Main } from "common/components/scaffold"

import { formatOperationType } from "accounting/utils/formatters"
import { useOperationDetailFields } from "./operation-detail-fields"
import { OperationDetailActions } from "./operation-detail-actions"

export const OperationDetail = () => {
  const navigate = useNavigate()
  const entity = useEntity()
  const match = useHashMatch("operation/:id")

  const { result, loading } = useQuery(api.getOperationDetail, {
    key: "operation-detail",
    params: [entity.id, parseInt(match?.params.id ?? "")],
  })

  const operation = result?.data

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  const fields = useOperationDetailFields(operation)

  return (
    <Portal onClose={closeDialog}>
      <Dialog
        onClose={closeDialog}
        header={
          operation && (
            <div className={css["operation-detail-header"]}>
              <Dialog.Title>
                {formatOperationType(operation.type)} n°{operation.id}
              </Dialog.Title>
              <OperationBadge status={operation.status} />
            </div>
          )
        }
        footer={
          <OperationDetailActions
            operation={operation}
            closeDialog={closeDialog}
          />
        }
      >
        <Main>
          {loading ? (
            <LoaderOverlay />
          ) : (
            <>
              <Grid className={css["operation-detail-fields"]}>
                {fields.map(({ label, value }) => (
                  <div key={label}>
                    <Text className={css["field-label"]}>{label}</Text>
                    <Text className={css["field-value"]}>{value}</Text>
                  </div>
                ))}
              </Grid>
            </>
          )}
        </Main>
      </Dialog>
    </Portal>
  )
}
