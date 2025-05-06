import { Column, Cell } from "common/components/table2"
import { useTranslation } from "react-i18next"
import { OperationBadge } from "./components/operation-badge"
import { formatDate, formatNumber, formatPeriod } from "common/utils/formatters"
import { Text } from "common/components/text"
import {
  formatOperationCreditOrDebit,
  getOperationEntity,
  isOperationDebit,
} from "./operations.utils"
import * as api from "accounting/api/operations"
import {
  Operation,
  OperationDebitOrCredit,
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
import useEntity from "common/hooks/entity"

type UseOperationsColumnsProps = {
  onClickSector: (sector: string) => void
}
export const useOperationsBiofuelsColumns = ({
  onClickSector,
}: UseOperationsColumnsProps) => {
  const { t } = useTranslation()
  const { unit } = useUnit()
  const currentEntity = useEntity()
  const columns: Column<Operation>[] = [
    {
      header: t("Statut"),
      cell: (item) => <OperationBadge status={item.status} />,
      style: {
        flex: "0 0 137px",
      },
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
    },
    {
      header: t("Biocarburant"),
      cell: (item) => <Cell text={item.biofuel} />,
    },
    {
      header: t("Catégorie"),
      cell: (item) => <Cell text={item.customs_category} />,
    },
    {
      header: t("Date"),
      cell: (item) => <Cell text={formatDate(item.created_at)} />,
    },
    {
      header: t("Dépôt"),
      cell: (item) => {
        const depot =
          item.type === OperationType.CESSION ? item.from_depot : item.to_depot
        return <Cell text={depot?.name ?? "-"} />
      },
    },
    {
      header: t("Opération"),
      cell: (item) => <Cell text={formatOperationType(item.type)} />,
    },
    {
      header: t("De/à"),
      cell: (item) => {
        const entity = getOperationEntity(item, currentEntity.id)
        return (
          <Cell
            text={
              item.type === OperationType.CESSION ||
              item.type === OperationType.ACQUISITION ||
              item.type === OperationType.TRANSFERT
                ? entity.name
                : "-"
            }
          />
        )
      },
    },
    {
      header: `${t("Quantité")} (${unit.toUpperCase()})`,
      cell: (item) =>
        isOperationDebit(item, currentEntity.id) ? (
          <Text
            size="sm"
            fontWeight="semibold"
            className={cl(
              styles["operation-debit"],
              item.status === OperationsStatus.REJECTED &&
                styles["operation--rejected"]
            )}
          >
            -
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
