import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { useMutation, useQuery } from "common/hooks/async"
import { useNavigate } from "react-router-dom"
import * as api from "accounting/api"
import * as apiAccounting from "accounting/api"
import { findDepots } from "carbure/api"
import useEntity from "carbure/hooks/entity"
import { useHashMatch } from "common/components/hash-route"
import {
  getOperationEntity,
  getOperationQuantity,
} from "accounting/operations/operations.utils"
import { OperationBadge } from "accounting/operations/components/operation-badge"
import css from "./operation-detail.module.css"
import { Text } from "common/components/text"
import { Trans, useTranslation } from "react-i18next"
import { Grid, LoaderOverlay, Main } from "common/components/scaffold"
import { formatDate, formatNumber } from "common/utils/formatters"
import { compact } from "common/utils/collection"
import { Button } from "common/components/button2"
import {
  useAcceptOperation,
  useDeleteOperation,
  useRejectOperation,
} from "./operation-detail.hooks"
import { Form, useForm } from "common/components/form2"
import { useNotify } from "common/components/notifications"
import { Depot, UserRole } from "carbure/types"
import { formatOperationType, formatSector } from "accounting/utils/formatters"
import { OperationsStatus, OperationType } from "accounting/types"
import { Autocomplete } from "common/components/autocomplete2"
import { useUnit } from "common/hooks/unit"

export const OperationDetail = () => {
  const navigate = useNavigate()
  const entity = useEntity()
  const { t } = useTranslation()
  const notify = useNotify()
  const { formatUnit } = useUnit()
  const match = useHashMatch("operation/:id")
  const { value, bind, setField } = useForm<{
    to_depot?: Pick<Depot, "id" | "name">
  }>({
    to_depot: undefined,
  })

  const { result, loading } = useQuery(api.getOperationDetail, {
    key: "operation-detail",
    params: [entity.id, parseInt(match?.params.id ?? "")],
    onSuccess: (result) => {
      setField("to_depot", result?.data?.to_depot)
    },
  })

  const operation = result?.data
  const canUpdateOperation =
    entity.hasRights(UserRole.ReadWrite) || entity.hasRights(UserRole.Admin)

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  const { execute: deleteOperation, loading: deleteOperationLoading } =
    useDeleteOperation({
      operation,
      onDeleteOperation: closeDialog,
    })

  const { execute: acceptOperation, loading: acceptOperationLoading } =
    useAcceptOperation({
      operation,
      onAcceptOperation: closeDialog,
    })

  const { execute: rejectOperation, loading: rejectOperationLoading } =
    useRejectOperation({
      operation,
      onRejectOperation: closeDialog,
    })

  const { execute: patchOperation, loading: patchOperationLoading } =
    useMutation(apiAccounting.patchOperation, {
      onError: () => {
        notify(
          t(
            "Une erreur est survenue lors de la mise à jour du dépot de livraison."
          ),
          {
            variant: "danger",
          }
        )
      },
    })

  const onAcceptOperation = () => {
    const patch = () => {
      if (operation && value.to_depot?.id !== operation?.to_depot?.id) {
        return patchOperation(entity.id, operation?.id, {
          to_depot: value.to_depot?.id,
        })
      }
      return Promise.resolve()
    }

    patch().then(() => {
      if (operation) {
        acceptOperation(entity.id, operation.id)
      }
    })
  }

  const fields = operation
    ? compact([
        { label: t("Filière"), value: formatSector(operation.sector) },
        {
          label: t("Date d'opération"),
          value: formatDate(operation?.created_at),
        },
        { label: t("Catégorie"), value: operation.customs_category },
        { label: t("Biocarburant"), value: operation.biofuel },
        {
          label: t("Quantité"),
          value: getOperationQuantity(
            operation,
            formatUnit(operation.quantity, 0)
          ),
        },
        {
          label: t("Tonnes CO2 eq evitées"),
          value: formatNumber(operation.avoided_emissions),
        },
        operation.type === OperationType.ACQUISITION && {
          label: t("Expéditeur"),
          value: getOperationEntity(operation)?.name ?? "-",
        },
        operation.type === OperationType.CESSION && {
          label: t("Destinataire"),
          value: getOperationEntity(operation)?.name ?? "-",
        },
        {
          label: t("Dépôt expéditeur"),
          value: operation.from_depot?.name ?? "-",
        },
        operation.type !== OperationType.DEVALUATION &&
          operation.type === OperationType.ACQUISITION &&
          operation.status !== OperationsStatus.PENDING && {
            label: t("Dépôt destinataire"),
            value: operation.to_depot?.name ?? "-",
          },
      ])
    : []

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
          <>
            {operation?.type === OperationType.ACQUISITION &&
              operation?.status === OperationsStatus.PENDING &&
              canUpdateOperation && (
                <>
                  <Button
                    customPriority="danger"
                    iconId="fr-icon-close-line"
                    onClick={() => {
                      rejectOperation(entity.id, operation.id)
                    }}
                    loading={rejectOperationLoading}
                  >
                    {t("Refuser")}
                  </Button>
                  <Button
                    customPriority="success"
                    iconId="fr-icon-check-line"
                    nativeButtonProps={{ form: "patch-operation" }}
                    loading={acceptOperationLoading || patchOperationLoading}
                  >
                    {t("Accepter")}
                  </Button>
                </>
              )}
            {operation?.type === OperationType.CESSION &&
              operation?.status === OperationsStatus.PENDING &&
              canUpdateOperation && (
                <Button
                  customPriority="danger"
                  iconId="fr-icon-close-line"
                  onClick={() => deleteOperation(entity.id, operation.id)}
                  loading={deleteOperationLoading}
                >
                  {t("Annuler le certificat de cession")}
                </Button>
              )}
          </>
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
                {operation?.type === OperationType.ACQUISITION &&
                  operation?.status === OperationsStatus.PENDING &&
                  canUpdateOperation && (
                    <div className={css["operation-detail-fields-depot"]}>
                      <Form id="patch-operation" onSubmit={onAcceptOperation}>
                        <Autocomplete
                          autoFocus
                          label={t("Dépot de livraison")}
                          hintText={t(
                            "Si le dépôt de livraison renseigné est inexact, vous pouvez le corriger ici."
                          )}
                          required
                          placeholder={t("Rechercher un site de livraison...")}
                          defaultOptions={
                            value.to_depot ? [value.to_depot] : []
                          }
                          getOptions={findDepots}
                          normalize={(depot) => ({
                            label: depot.name,
                            value: depot,
                          })}
                          {...bind("to_depot")}
                        />
                      </Form>
                    </div>
                  )}
              </Grid>
              {operation?.type === OperationType.ACQUISITION &&
                operation?.status === OperationsStatus.PENDING &&
                canUpdateOperation && (
                  <>
                    <Text>{t("Voulez-vous accepter ce certificat ?")}</Text>
                    <div>
                      <Text>
                        <Trans defaults="<b>Si vous l’acceptez</b>, celui-ci sera comptabilisé en acquisition et viendra alimenter votre solde." />
                      </Text>
                      <Text>
                        <Trans defaults="Si vous le <b>refusez</b>, celui-ci n’apparaîtra plus dans vos opérations en attente." />
                      </Text>
                    </div>
                  </>
                )}
              {operation?.type === OperationType.CESSION &&
                operation?.status === OperationsStatus.PENDING &&
                canUpdateOperation && (
                  <>
                    <Text>
                      {t("Voulez-vous annuler ce certificat de cession ?")}
                    </Text>
                    <Text>
                      {t(
                        "Vous pouvez annuler un certificat de cession, tant que celui-ci est encore en attente côté redevable."
                      )}
                    </Text>
                  </>
                )}
            </>
          )}
        </Main>
      </Dialog>
    </Portal>
  )
}
