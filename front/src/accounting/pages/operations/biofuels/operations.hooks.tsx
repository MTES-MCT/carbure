import { Column, Cell } from "common/components/table2"
import { useTranslation } from "react-i18next"
import { OperationBadge } from "accounting/components/operation-badge"
import { formatDate, formatNumber, formatPeriod } from "common/utils/formatters"
import { Text } from "common/components/text"
import { isSendingOperation } from "./operations.utils"
import * as api from "accounting/api/biofuels/operations"
import {
  OperationDebitOrCredit,
  OperationList,
  OperationOrder,
  OperationsFilter,
  OperationsQuery,
  OperationsStatus,
  OperationType,
} from "accounting/types"
import { useNormalizeSector } from "accounting/hooks/normalizers"
import {
  formatOperationCreditOrDebit,
  formatOperationStatus,
  formatOperationType,
  formatSector,
  formatTCO2Number,
} from "accounting/utils/formatters"
import styles from "../operations.module.css"
import cl from "clsx"
import { useUnit } from "common/hooks/unit"
import {
  DEFAULT_UNIT_OPERATION,
  FRACTION_DIGITS_LITERS,
} from "accounting/config"

type UseOperationsColumnsProps = {
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

export const useGetFilterOptions = (
  query: OperationsQuery,
  selectedEntityId?: number
) => {
  const { t } = useTranslation()
  const normalizeSector = useNormalizeSector()

  const getFilterOptions = async (filter: OperationsFilter) => {
    const { data } = await api.getOperationsFilters(
      filter,
      query,
      selectedEntityId
    )

    if (!data) {
      return []
    }

    if (filter === OperationsFilter.status) {
      return data?.map((item) => ({
        label: formatOperationStatus(item as OperationsStatus),
        value: item,
      }))
    }

    if (filter === OperationsFilter.sector) {
      return data?.map(normalizeSector)
    }

    if (filter === OperationsFilter.operation) {
      return data?.map((item) => ({
        label: t(formatOperationType(item as OperationType)),
        value: item,
      }))
    }

    if (filter === OperationsFilter.type) {
      return data?.map((item) => ({
        label: t(formatOperationCreditOrDebit(item as OperationDebitOrCredit)),
        value: item,
      }))
    }

    if (
      [OperationsFilter.period, OperationsFilter.durability_period].includes(
        filter
      )
    ) {
      return data?.map((item) => ({
        label: formatPeriod(item),
        value: item,
      }))
    }

    return data
  }

  return getFilterOptions
}
