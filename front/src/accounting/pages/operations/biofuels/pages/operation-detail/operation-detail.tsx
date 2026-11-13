import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { useQuery } from "common/hooks/async"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "accounting/api/biofuels/operations"
import useEntity from "common/hooks/entity"
import { useHashMatch } from "common/components/hash-route"
import { OperationBadge } from "accounting/components/operation-badge/operation-badge"
import css from "accounting/pages/operations/biofuels/components/operations-table/operations-table.module.css"
import { Text } from "common/components/text"
import { Grid, LoaderOverlay, Main } from "common/components/scaffold"

import { formatOperationType } from "accounting/utils/formatters"
import { useOperationDetailFields } from "./operation-detail-fields"
import { OperationDetailActions } from "./operation-detail-actions"
import { useSelectedEntity } from "common/providers/selected-entity-provider"
import { Button } from "common/components/button2"
import { useTranslation } from "react-i18next"

export const OperationDetail = () => {
  const navigate = useNavigate()
  const entity = useEntity()
  const match = useHashMatch("operation/:id")
  const { selectedEntityId } = useSelectedEntity()

  const { result, loading } = useQuery(api.getOperationDetail, {
    key: "operation-detail",
    params: [entity.id, parseInt(match?.params.id ?? ""), selectedEntityId],
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
                {fields.map(({ label, value, href, originalValue }) => (
                  <div key={label}>
                    {label && (
                      <Text className={css["field-label"]}>{label}</Text>
                    )}
                    <Text className={css["field-value"]}>
                      {href ? (
                        <Button
                          customPriority="link"
                          linkProps={{
                            to: href,
                            target: "_blank",
                          }}
                        >
                          {value}
                        </Button>
                      ) : originalValue != null ? (
                        <>
                          <del>{originalValue}</del> {value}
                        </>
                      ) : (
                        value
                      )}
                    </Text>
                  </div>
                ))}
              </Grid>
              {operation?.ghg_delta != null && (
                <CorrectedOperationLinks
                  ids={operation.corrected_operation_ids}
                />
              )}
            </>
          )}
        </Main>
      </Dialog>
    </Portal>
  )
}

export const CorrectedOperationLinks = ({ ids }: { ids?: number[] }) => {
  const { t } = useTranslation()
  const location = useLocation()

  if (!ids?.length) return null

  return (
    <ul className={css["operation-detail-corrected-links"]}>
      {ids.map((id) => (
        <li key={id}>
          <Button
            customPriority="link"
            linkProps={{
              to: `${location.pathname}${location.search}#operation/${id}`,
              target: "_blank",
            }}
          >
            {t("Opération corrigée n° {{id}}", { id })}
          </Button>
        </li>
      ))}
    </ul>
  )
}
