import { OperationBadge } from "accounting/components/operation-badge"
import {
  DEFAULT_UNIT_OPERATION,
  FRACTION_DIGITS_LITERS,
} from "accounting/config"
import {
  OperationList,
  OperationOrder,
  OperationsStatus,
  OperationType,
} from "accounting/types"
import {
  formatOperationType,
  formatSector,
  formatTCO2Number,
} from "accounting/utils/formatters"
import { useUnit } from "common/hooks/unit"
import { formatDate, formatNumber } from "common/utils/formatters"
import { Cell, Column } from "common/components/table2"
import { Text } from "common/components/text"
import { useTranslation } from "react-i18next"
import cl from "clsx"
import styles from "./operations-table.module.css"
import { isSendingOperation } from "../../operations.utils"

export type UseOperationsColumnsProps = {
  onClickSector: (sector: string) => void
}

const displayValueDebitOrCredit = (
  value: number | string,
  isOperationDebit: boolean,
  isOperationRejected: boolean,
  isOperationYearlyBalance: boolean
) => {
  const operator = isOperationDebit ? "-" : "+"

  return isOperationDebit ? (
    <Text
      size="sm"
      fontWeight="semibold"
      className={cl(
        styles["operation-debit"],
        isOperationRejected && styles["operation--rejected"],
        isOperationYearlyBalance && styles["field-label"]
      )}
    >
      {operator}
      {value}
    </Text>
  ) : (
    <Text
      size="sm"
      fontWeight="semibold"
      className={cl(
        styles["operation-credit"],
        isOperationRejected && styles["operation--rejected"],
        isOperationYearlyBalance && styles["field-label"]
      )}
    >
      {operator}
      {value}
    </Text>
  )
}

export const useOperationsBiofuelsColumns = ({
  onClickSector,
}: UseOperationsColumnsProps) => {
  const { t } = useTranslation()
  const { unit } = useUnit(DEFAULT_UNIT_OPERATION)

  const columns: Column<OperationList>[] = [
    {
      header: t("Statut"),
      cell: (item) => <OperationBadge status={item.status} />,
      style: {
        flex: "0 0 137px",
      },
      key: OperationOrder.status,
    },
    {
      header: t("Filière"),
      cell: (item) => (
        <Text
          size="sm"
          fontWeight="bold"
          className={styles["operation-table__sector"]}
          is="button"
          componentProps={{
            onClick: () => onClickSector(item.sector),
          }}
        >
          {formatSector(item.sector)}
        </Text>
      ),
      key: OperationOrder.sector,
    },
    {
      header: t("Biocarburant"),
      cell: (item) => <Cell text={item.biofuel?.code} />,
      key: OperationOrder.biofuel,
    },
    {
      header: t("Catégorie"),
      cell: (item) => <Cell text={item.customs_category} />,
      key: OperationOrder.customs_category,
    },
    {
      header: t("Date de création"),
      cell: (item) => <Cell text={formatDate(item.created_at)} />,
      key: OperationOrder.created_at,
    },
    {
      header: t("Dépôt"),
      cell: (item) => {
        return <Cell text={item._depot ?? "-"} />
      },
      key: OperationOrder.depot,
    },
    {
      header: t("Opération"),
      cell: (item) => <Cell text={formatOperationType(item.type, item.year)} />,
      key: OperationOrder.type,
    },
    {
      header: t("De/à"),
      cell: (item) => {
        return <Cell text={item._entity ?? "-"} />
      },
      key: OperationOrder.from_to,
    },
    {
      key: OperationOrder.volume,
      header: `${t("Quantité")} (${unit.toUpperCase()})`,
      style: {
        minWidth: "140px",
      },
      cell: (item) => {
        const calculatedQuantity = Math.abs(item.volume)
        const formattedQuantity = formatNumber(calculatedQuantity, {
          fractionDigits: FRACTION_DIGITS_LITERS,
        })
        return displayValueDebitOrCredit(
          formattedQuantity,
          isSendingOperation(item.volume),
          item.status === OperationsStatus.REJECTED,
          item.type === OperationType.YEARLY_BALANCE
        )
      },
    },
    {
      header: `${t("tCO2 évitées")}`,
      cell: (item) => {
        const calculatedAvoidedEmissions = Math.abs(item.avoided_emissions)
        const formattedAvoidedEmissions = formatTCO2Number(
          calculatedAvoidedEmissions
        )
        return displayValueDebitOrCredit(
          formattedAvoidedEmissions,
          isSendingOperation(item.volume),
          item.status === OperationsStatus.REJECTED,
          item.type === OperationType.YEARLY_BALANCE
        )
      },
      style: {
        minWidth: "140px",
      },
    },
  ]

  return columns
}
