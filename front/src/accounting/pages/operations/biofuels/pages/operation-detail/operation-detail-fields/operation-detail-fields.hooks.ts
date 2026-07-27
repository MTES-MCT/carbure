import { Operation, OperationType } from "accounting/types"
import { formatSector, formatTCO2Number } from "accounting/utils/formatters"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { formatQuantityDisplay } from "./operation-detail-fields.utils"
import { formatDate, formatPeriod } from "common/utils/formatters"
import { useUnit } from "common/hooks/unit"
import { DEFAULT_UNIT_OPERATION } from "accounting/config"
import { compact } from "common/utils/collection"
import { formatValue } from "../../../operations.utils"

export const useOperationDetailFields = (operation?: Operation) => {
  const { t } = useTranslation()
  const { formatUnit } = useUnit(DEFAULT_UNIT_OPERATION)
  const exportationOrExpeditionFields =
    useExportationOrExpeditionFields(operation)

  return useMemo(() => {
    if (!operation) return []

    // Determine operation direction: positive quantity = receiving, negative = sending
    const isReceiver = (operation?.quantity ?? 0) > 0
    const isSender = (operation?.quantity ?? 0) < 0

    // Define all possible conditional fields
    const fields = compact([
      { label: t("Filière"), value: formatSector(operation.sector) },
      {
        label: t("Date d'opération"),
        value: formatDate(operation?.created_at),
      },
      { label: t("Catégorie"), value: operation.customs_category },
      { label: t("Biocarburant"), value: operation.biofuel?.code },
      {
        label: t("Quantité"),
        value: formatQuantityDisplay(operation, formatUnit, false),
      },
      operation.type === OperationType.INCORPORATION &&
        operation.renewable_energy_share !== 1 && {
          label: t("Quantité renouvelable"),
          value: formatQuantityDisplay(operation, formatUnit, true),
        },
      {
        label: t("Tonnes CO2 eq évitées"),
        value: formatTCO2Number(
          formatValue(operation, operation.avoided_emissions)
        ),
      },
      operation.type === OperationType.TRANSFERT &&
        isReceiver && {
          label: t("Expéditeur"),
          value: operation._entity ?? "-",
        },
      operation.type === OperationType.TRANSFERT &&
        isSender && {
          label: t("Destinataire"),
          value: operation._entity ?? "-",
        },
      ...exportationOrExpeditionFields,
      typeof operation.durability_period === "string" && {
        label:
          operation.type === OperationType.EXPIRATION
            ? t("Année de durabilité des volumes expirés")
            : t("Déclaration de durabilité"),
        value:
          operation.type === OperationType.EXPIRATION
            ? operation.durability_period
            : formatPeriod(operation.durability_period),
      },
      typeof operation.year === "number" && {
        label: t("Année"),
        value: operation.year,
      },
      operation.type === OperationType.TENEUR && {
        label: t("Objectif de filière IRICC"),
        value: formatSector(operation.objective_sector ?? operation.sector),
      },
    ])

    return fields
  }, [operation, t, formatUnit, exportationOrExpeditionFields])
}

const useExportationOrExpeditionFields = (operation?: Operation) => {
  const { t } = useTranslation()

  return useMemo(() => {
    const isExportationOrExpedition = [
      OperationType.EXPORTATION,
      OperationType.EXPEDITION,
    ].includes(operation?.type as OperationType)

    if (!operation || !isExportationOrExpedition) return []

    return [
      {
        label: t("Destinataire"),
        value: operation.export_recipient ?? "-",
      },
      {
        label: t("Dépôt expéditeur"),
        value: operation.from_depot ? operation.from_depot.name : "-",
      },
      operation.export_country && {
        label: t("Pays d'exportation"),
        value: operation.export_country ? operation.export_country.name : "-",
      },
    ]
  }, [operation, t])
}
