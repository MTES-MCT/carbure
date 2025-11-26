import { Operation, OperationType } from "accounting/types"
import { formatSector } from "accounting/utils/formatters"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import {
  formatQuantityDisplay,
  formatValue,
} from "./operation-detail-fields.utils"
import { formatDate, formatNumber, formatPeriod } from "common/utils/formatters"
import { useUnit } from "common/hooks/unit"
import { compact } from "common/utils/collection"

export const useOperationDetailFields = (operation?: Operation) => {
  const { t } = useTranslation()
  const { formatUnit } = useUnit()
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
      { label: t("Biocarburant"), value: operation.biofuel },
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
        label: t("Tonnes CO2 eq evitées"),
        value: formatNumber(
          formatValue(operation, operation.avoided_emissions),
          {
            fractionDigits: 0,
          }
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
        label: t("Déclaration de durabilité"),
        value: formatPeriod(operation.durability_period),
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
