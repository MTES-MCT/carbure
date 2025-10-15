import { Column, Cell } from "common/components/table2"
import { useTranslation } from "react-i18next"
import { OperationBadge } from "accounting/components/operation-badge"
import { formatDate, formatNumber, formatPeriod } from "common/utils/formatters"
import { Text } from "common/components/text"
import { getOperationEntity, isOperationDebit } from "./operations.utils"
import * as api from "accounting/api/elec/operations"
import {
  ElecOperation,
  OperationDebitOrCredit,
  OperationsFilter,
  ElecOperationsQuery,
  ElecOperationsStatus,
  ElecOperationType,
  ElecOperationOrder,
} from "accounting/types"
import {
  formatOperationCreditOrDebit,
  formatOperationStatus,
  formatOperationType,
} from "accounting/utils/formatters"
import styles from "../operations.module.css"
import cl from "clsx"
import { useUnit } from "common/hooks/unit"
import { Unit } from "common/types"

export const useOperationsElecColumns = () => {
  const { t } = useTranslation()
  const { unit } = useUnit(Unit.MJ)

  const columns: Column<ElecOperation>[] = [
    {
      header: t("Statut"),
      cell: (item) => <OperationBadge status={item.status} />,
      key: ElecOperationOrder.status,
      style: {
        flex: "0 0 137px",
      },
    },
    {
      header: t("Date"),
      key: ElecOperationOrder.created_at,
      cell: (item) => <Cell text={formatDate(item.created_at)} />,
    },
    {
      header: t("Opération"),
      key: ElecOperationOrder.operation,
      cell: (item) => <Cell text={formatOperationType(item.type)} />,
    },
    {
      header: t("De/à"),
      key: ElecOperationOrder.from_to,
      cell: (item) => {
        const entity = getOperationEntity(item)
        return (
          <Cell
            text={
              item.type === ElecOperationType.CESSION ||
              item.type === ElecOperationType.ACQUISITION
                ? entity.name
                : "-"
            }
          />
        )
      },
    },
    {
      header: `${t("Quantité")} (${unit.toUpperCase()})`,
      key: ElecOperationOrder.quantity,
      cell: (item) =>
        isOperationDebit(item.type) ? (
          <Text
            size="sm"
            fontWeight="semibold"
            className={cl(
              styles["operation-debit"],
              item.status === ElecOperationsStatus.REJECTED &&
                styles["operation--rejected"]
            )}
          >
            -
            {formatNumber(item.quantity ?? 0, {
              fractionDigits: 0,
            })}
          </Text>
        ) : (
          <Text
            size="sm"
            fontWeight="semibold"
            className={cl(
              styles["operation-credit"],
              item.status === ElecOperationsStatus.REJECTED &&
                styles["operation--rejected"]
            )}
          >
            +
            {formatNumber(item.quantity ?? 0, {
              fractionDigits: 0,
            })}
          </Text>
        ),
    },
  ]

  return columns
}

export const useGetFilterOptions = (query: ElecOperationsQuery) => {
  const { t } = useTranslation()

  const getFilterOptions = async (filter: string) => {
    const { data } = await api.getOperationsFilters(filter, query)

    if (!data) {
      return []
    }

    if (filter === OperationsFilter.status) {
      return data?.map((item) => ({
        label: formatOperationStatus(item as ElecOperationsStatus),
        value: item,
      }))
    }

    if (filter === OperationsFilter.operation) {
      return data?.map((item) => ({
        label: t(formatOperationType(item as ElecOperationType)),
        value: item,
      }))
    }

    if (filter === OperationsFilter.type) {
      return data?.map((item) => ({
        label: t(formatOperationCreditOrDebit(item as OperationDebitOrCredit)),
        value: item,
      }))
    }

    if (filter === OperationsFilter.period) {
      return data?.map((item) => ({
        label: formatPeriod(item),
        value: item,
      }))
    }

    return data
  }

  return getFilterOptions
}
