import { Column, Cell } from "common/components/table2"
import { useTranslation } from "react-i18next"
import { OperationBadge } from "./components/operation-badge"
import { formatDate, formatNumber } from "common/utils/formatters"
import { Text } from "common/components/text"
import {
  formatOperationCreditOrDebit,
  formatOperationStatus,
  formatOperationType,
  formatSector,
  getOperationEntity,
  isOperationDebit,
} from "./operations.utils"
import * as api from "./api"
import {
  Operation,
  OperationDebitOrCredit,
  OperationsFilter,
  OperationsQuery,
  OperationsStatus,
  OperationType,
} from "./types"
type UseOperationsColumnsProps = {
  onClickSector: (sector: string) => void
}
export const useOperationsColumns = ({
  onClickSector,
}: UseOperationsColumnsProps) => {
  const { t } = useTranslation()

  const columns: Column<Operation>[] = [
    {
      header: t("Statut"),
      cell: (item) => <OperationBadge status={item.status} />,
    },
    {
      header: t("Filière"),
      cell: (item) => (
        <Text
          size="sm"
          fontWeight="bold"
          style={{ color: "var(--info-425-625)" }}
          is="button"
          componentProps={{
            onClick: () => onClickSector(item.sector),
          }}
        >
          {t(formatSector(item.sector))}
        </Text>
      ),
    },
    {
      header: t("Biocarburant"),
      cell: (item) => item.biofuel,
    },
    {
      header: t("Catégorie"),
      cell: (item) => item.customs_category,
    },
    {
      header: t("Date"),
      cell: (item) => formatDate(item.created_at),
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
      cell: (item) => <Cell text={t(formatOperationType(item.type))} />,
    },
    {
      header: t("De/à"),
      cell: (item) => {
        const entity = getOperationEntity(item)
        return (
          <Cell
            text={
              item.type === OperationType.CESSION ||
              item.type === OperationType.ACQUISITION
                ? entity.name
                : "-"
            }
          />
        )
      },
    },
    {
      key: "volume",
      header: t("Volume"),
      cell: (item) =>
        isOperationDebit(item.type) ? (
          <Text
            size="sm"
            fontWeight="semibold"
            style={{ color: "var(--text-default-error)" }}
          >
            -{formatNumber(Number(item.volume))}
          </Text>
        ) : (
          <Text
            size="sm"
            fontWeight="semibold"
            style={{ color: "var(--text-default-success)" }}
          >
            +{formatNumber(Number(item.volume))}
          </Text>
        ),
    },
  ]

  return columns
}

export const useGetFilterOptions = (query: OperationsQuery) => {
  const { t } = useTranslation()

  const getFilterOptions = async (filter: string) => {
    const { data } = await api.getOperationsFilters(filter, query)

    if (!data) {
      return []
    }

    if (filter === OperationsFilter.status) {
      return data?.map((item) => ({
        label: t(formatOperationStatus(item as OperationsStatus)),
        value: item,
      }))
    }

    if (filter === OperationsFilter.sector) {
      return data?.map((item) => ({
        label: t(formatSector(item)),
        value: item,
      }))
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

    return data
  }

  return getFilterOptions
}
