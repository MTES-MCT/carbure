import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { useMutation, useQuery } from "common/hooks/async"
import { useNavigate } from "react-router-dom"
import * as api from "accounting/api/biofuels/operations"
import { findDepots } from "common/api"
import useEntity from "common/hooks/entity"
import { useHashMatch } from "common/components/hash-route"
import { getOperationQuantity, isOperationDebit } from "../../operations.utils"
import { OperationBadge } from "accounting/components/operation-badge/operation-badge"
import css from "../../../operations.module.css"
import { Text } from "common/components/text"
import { Trans, useTranslation } from "react-i18next"
import { Grid, LoaderOverlay, Main } from "common/components/scaffold"
import {
  CONVERSIONS,
  formatDate,
  formatNumber,
  roundNumber,
  formatPeriod,
} from "common/utils/formatters"
import { compact } from "common/utils/collection"
import { Button } from "common/components/button2"
import {
  useAcceptOperation,
  useDeleteOperation,
  useRejectOperation,
} from "./operation-detail.hooks"
import { Form, useForm } from "common/components/form2"
import { useNotify } from "common/components/notifications"
import { Autocomplete } from "common/components/autocomplete2"
import { Depot, ExtendedUnit, UserRole } from "common/types"
import { useUnit } from "common/hooks/unit"
import { formatOperationType, formatSector } from "accounting/utils/formatters"
import { OperationsStatus, OperationType } from "accounting/types"

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
    useMutation(api.patchOperation, {
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

  const {
    execute: validateDraftTransfer,
    loading: validateDraftTransferLoading,
  } = useMutation(api.patchOperation, {
    invalidates: ["operations"],
    onSuccess: () => {
      notify(t("Le transfert a été réalisé avec succès."), {
        variant: "success",
      })
      closeDialog()
    },
    onError: () => {
      notify(t("Une erreur est survenue lors du transfert."), {
        variant: "danger",
      })
    },
  })

  const onAcceptOperation = () => {
    const patch = () => {
      if (
        operation &&
        operation.type === OperationType.ACQUISITION &&
        value.to_depot?.id !== operation?.to_depot?.id
      ) {
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

  // Format the value only for the incorporation operation
  const formatValue = (value: number) => {
    return operation?.type === OperationType.INCORPORATION
      ? value * operation.renewable_energy_share
      : value
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
          value: `${getOperationQuantity(
            operation,
            formatUnit(operation.quantity)
          )} / ${getOperationQuantity(
            operation,
            formatUnit(CONVERSIONS.energy.MJ_TO_GJ(operation.quantity_mj), {
              unit: ExtendedUnit.GJ,
            })
          )}`,
        },
        operation.type === OperationType.INCORPORATION &&
          operation.renewable_energy_share !== 1 && {
            label: t("Quantité renouvelable"),
            value: `${getOperationQuantity(
              operation,
              formatUnit(roundNumber(formatValue(operation.quantity), 2))
            )} / ${getOperationQuantity(
              operation,
              formatUnit(
                CONVERSIONS.energy.MJ_TO_GJ(
                  roundNumber(formatValue(operation.quantity_mj), 2)
                ),
                {
                  unit: ExtendedUnit.GJ,
                }
              )
            )}`,
          },
        {
          label: t("Tonnes CO2 eq evitées"),
          value: formatNumber(formatValue(operation.avoided_emissions), {
            fractionDigits: 0,
          }),
        },
        (operation.type === OperationType.ACQUISITION ||
          (operation.type === OperationType.TRANSFERT &&
            operation?.quantity > 0)) && {
          label: t("Expéditeur"),
          value: operation._entity ?? "-",
        },
        [OperationType.CESSION, OperationType.TRANSFERT].includes(
          operation.type as OperationType
        ) &&
          operation.quantity < 0 && {
            label: t("Destinataire"),
            value: operation._entity ?? "-",
          },
        operation.type !== OperationType.TENEUR &&
          operation.type !== OperationType.TRANSFERT && {
            label: t("Dépôt expéditeur"),
            value: operation._depot ?? "-",
          },
        operation.type !== OperationType.DEVALUATION &&
          operation.type === OperationType.ACQUISITION &&
          operation.status !== OperationsStatus.PENDING && {
            label: t("Dépôt destinataire"),
            value: operation._depot ?? "-",
          },
        typeof operation.durability_period === "string" && {
          label: t("Déclaration de durabilité"),
          value: formatPeriod(operation.durability_period),
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
            {/* Display reject/accept button in two cases :
             - Acquisition operation
             - Transfer operation only if it's a credit operation
            */}
            {(operation?.type === OperationType.ACQUISITION ||
              (operation?.type === OperationType.TRANSFERT &&
                !isOperationDebit(operation?.quantity))) &&
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
                    type="submit"
                  >
                    {t("Accepter")}
                  </Button>
                </>
              )}
            {isOperationDebit(operation?.quantity ?? 0) &&
              operation?.status === OperationsStatus.PENDING &&
              canUpdateOperation && (
                <Button
                  customPriority="danger"
                  iconId="fr-icon-close-line"
                  onClick={() => deleteOperation(entity.id, operation.id)}
                  loading={deleteOperationLoading}
                >
                  {t("Annuler le certificat")}
                </Button>
              )}

            {/* Display cancel/transfer button only if operation is a DRAFT transfer */}
            {operation?.status === OperationsStatus.DRAFT &&
              operation?.type === OperationType.TRANSFERT && (
                <>
                  <Button
                    customPriority="danger"
                    iconId="fr-icon-close-line"
                    onClick={() => deleteOperation(entity.id, operation.id)}
                    loading={deleteOperationLoading}
                  >
                    {t("Annuler la transaction")}
                  </Button>
                  <Button
                    priority="primary"
                    onClick={() =>
                      validateDraftTransfer(entity.id, operation.id, {
                        status: OperationsStatus.PENDING,
                      })
                    }
                    loading={validateDraftTransferLoading}
                  >
                    {t("Transférer")}
                  </Button>
                </>
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
                <Form
                  id="patch-operation"
                  onSubmit={onAcceptOperation}
                  className={css["operation-detail-fields-depot"]}
                >
                  {operation?.type === OperationType.ACQUISITION &&
                    operation?.status === OperationsStatus.PENDING &&
                    canUpdateOperation && (
                      <div>
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
                      </div>
                    )}
                </Form>
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
