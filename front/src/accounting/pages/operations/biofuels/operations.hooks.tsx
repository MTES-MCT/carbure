import { Column, Cell } from "common/components/table2"
import { useTranslation } from "react-i18next"
import { OperationBadge } from "./components/operation-badge"
import { formatDate, formatNumber, formatPeriod } from "common/utils/formatters"
import { Text } from "common/components/text"
import {
  formatOperationCreditOrDebit,
  isOperationDebit,
} from "./operations.utils"
import * as api from "accounting/api/operations"
import {
  Operation,
  OperationDebitOrCredit,
  OperationOrder,
  OperationsFilter,
  OperationsQuery,
  OperationsStatus,
  OperationType,
} from "accounting/types"
import { useNormalizeSector } from "accounting/hooks/normalizers"
import {
  formatOperationStatus,
  formatOperationType,
  formatSector,
} from "accounting/utils/formatters"
import styles from "./operations.module.css"
import cl from "clsx"
import { useUnit } from "common/hooks/unit"

type UseOperationsColumnsProps = {
  onClickSector: (sector: string) => void
}
export const useOperationsBiofuelsColumns = ({
  onClickSector,
}: UseOperationsColumnsProps) => {
  const { t } = useTranslation()
  const { unit } = useUnit()

  const columns: Column<Operation>[] = [
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
      cell: (item) => <Cell text={item.biofuel} />,
      key: OperationOrder.biofuel,
    },
    {
      header: t("Catégorie"),
      cell: (item) => <Cell text={item.customs_category} />,
      key: OperationOrder.customs_category,
    },
    {
      header: t("Date"),
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
      cell: (item) => <Cell text={formatOperationType(item.type)} />,
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
      key: OperationOrder.quantity,
      header: `${t("Quantité")} (${unit.toUpperCase()})`,
      cell: (item) =>
        isOperationDebit(item.quantity) ? (
          <Text
            size="sm"
            fontWeight="semibold"
            className={cl(
              styles["operation-debit"],
              item.status === OperationsStatus.REJECTED &&
                styles["operation--rejected"]
            )}
          >
            {formatNumber(
              item.type === OperationType.INCORPORATION
                ? item.quantity_renewable
                : item.quantity,
              {
                fractionDigits: 0,
              }
            )}
          </Text>
        ) : (
          <Text
            size="sm"
            fontWeight="semibold"
            className={cl(
              styles["operation-credit"],
              item.status === OperationsStatus.REJECTED &&
                styles["operation--rejected"]
            )}
          >
            +
            {formatNumber(
              item.type === OperationType.INCORPORATION
                ? item.quantity_renewable
                : item.quantity,
              {
                fractionDigits: 0,
              }
            )}
          </Text>
        ),
    },
  ]

  return columns
}

export const useGetFilterOptions = (query: OperationsQuery) => {
  const { t } = useTranslation()
  const normalizeSector = useNormalizeSector()

  const getFilterOptions = async (filter: string) => {
    const { data } = await api.getOperationsFilters(filter, query)

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
