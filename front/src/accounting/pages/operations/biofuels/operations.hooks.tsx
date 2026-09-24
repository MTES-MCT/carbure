import { useTranslation } from "react-i18next"
import { formatPeriod } from "common/utils/formatters"
import * as api from "accounting/api/biofuels/operations"
import {
  OperationDebitOrCredit,
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
} from "accounting/utils/formatters"

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
