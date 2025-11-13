import { Operation } from "accounting/types"
import { formatSector } from "accounting/utils/formatters"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { formatValue, getFields } from "./operation-detail-fields.utils"
import { CONVERSIONS, formatDate, formatNumber } from "common/utils/formatters"
import { getOperationQuantity } from "../../../operations.utils"
import { useUnit } from "common/hooks/unit"
import { ExtendedUnit } from "common/types"
import { Field, OperationDetailField } from "./operation-detail-fields.types"
import {
  MAPPING_FIELDS_RECEIVER,
  MAPPING_FIELDS_SENDER,
} from "./operation-detail-fields.config"

export const useOperationDetailFields = (operation?: Operation) => {
  const commonFields = useCommonFields(operation)
  const conditionalFields = useConditionalFields(operation)

  const fields = useMemo<Field[]>(() => {
    if (!operation) return []

    // Combine common and conditional fields, filtering out fields with condition === false or undefined
    return [...commonFields, ...conditionalFields].filter(
      ({ condition }) => condition === undefined || condition
    )
  }, [operation, commonFields, conditionalFields])

  return fields
}

// Fields that are always displayed regardless of operation type or receiving/sending operation
const useCommonFields = (operation?: Operation) => {
  const { t } = useTranslation()
  const { formatUnit } = useUnit()

  return useMemo<Field[]>(() => {
    if (!operation) return []

    return [
      {
        name: OperationDetailField.SECTOR,
        label: t("Filière"),
        value: formatSector(operation.sector),
      },
      {
        name: OperationDetailField.OPERATION_DATE,
        label: t("Date d'opération"),
        value: formatDate(operation?.created_at),
      },
      {
        name: OperationDetailField.CUSTOMS_CATEGORY,
        label: t("Catégorie"),
        value: operation.customs_category,
      },
      {
        name: OperationDetailField.BIOFUEL,
        label: t("Biocarburant"),
        value: operation.biofuel,
      },
      {
        name: OperationDetailField.QUANTITY,
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
      {
        name: OperationDetailField.AVOIDED_EMISSIONS,
        label: t("Tonnes CO2 eq evitées"),
        value: formatNumber(
          formatValue(operation, operation.avoided_emissions),
          {
            fractionDigits: 0,
          }
        ),
      },
    ]
  }, [operation, t, formatUnit])
}

// Fields that are conditionally displayed based on operation type and receiving/sending operation
const useConditionalFields = (operation?: Operation) => {
  const { t } = useTranslation()
  const { formatUnit } = useUnit()

  return useMemo<Field[]>(() => {
    if (!operation) return []

    // Define all possible conditional fields
    const fields = [
      {
        name: OperationDetailField.RENEWABLE_ENERGY_QUANTITY,
        label: t("Quantité renouvelable"),
        value: `${getOperationQuantity(
          operation,
          formatUnit(formatValue(operation, operation.quantity), {
            fractionDigits: 2,
          })
        )} / ${getOperationQuantity(
          operation,
          formatUnit(
            CONVERSIONS.energy.MJ_TO_GJ(
              formatValue(operation, operation.quantity_mj)
            ),
            {
              unit: ExtendedUnit.GJ,
              fractionDigits: 2,
            }
          )
        )}`,
      },
    ]

    // Determine operation direction: positive quantity = receiving, negative = sending
    const isReceiver = (operation.quantity ?? 0) > 0
    const mappingFields = isReceiver
      ? MAPPING_FIELDS_RECEIVER
      : MAPPING_FIELDS_SENDER

    // Filter fields based on the configuration mapping for this operation type and direction
    return getFields(operation, fields, mappingFields)
  }, [operation, t, formatUnit])
}
