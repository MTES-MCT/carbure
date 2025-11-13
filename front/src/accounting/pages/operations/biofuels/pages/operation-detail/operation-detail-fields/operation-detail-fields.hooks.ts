import { Operation, OperationType } from "accounting/types"
import { formatSector } from "accounting/utils/formatters"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import {
  formatQuantityDisplay,
  formatValue,
  getFields,
} from "./operation-detail-fields.utils"
import {
  CONVERSIONS,
  formatDate,
  formatNumber,
  formatPeriod,
  roundNumber,
} from "common/utils/formatters"
import { getOperationQuantity } from "../../../operations.utils"
import { useUnit } from "common/hooks/unit"
import { ExtendedUnit } from "common/types"
import { compact } from "common/utils/collection"

export const useOperationDetailFields = (operation?: Operation) => {
  const fields = useFields(operation)

  return fields
}

const useFields = (operation?: Operation) => {
  const { t } = useTranslation()
  const { formatUnit } = useUnit()

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
      (operation.type === OperationType.EXPORTATION ||
        operation.type === OperationType.EXPEDITION) && {
        label: t("Destinataire"),
        value: operation.export_recipient ?? "-",
      },
      [OperationType.EXPORTATION, OperationType.EXPEDITION].includes(
        operation.type as OperationType
      ) && {
        label: t("Dépôt expéditeur"),
        value: operation.from_depot ? operation.from_depot.name : "-",
      },
      [OperationType.EXPORTATION, OperationType.EXPEDITION].includes(
        operation.type as OperationType
      ) &&
        operation.export_country && {
          label: t("Pays d'exportation"),
          value: operation.export_country ? operation.export_country.name : "-",
        },
      typeof operation.durability_period === "string" && {
        label: t("Déclaration de durabilité"),
        value: formatPeriod(operation.durability_period),
      },
    ])

    return fields
  }, [operation, t, formatUnit])
}
