import { FilterMultiSelectProps } from "common/molecules/filter-select"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { useMatch } from "react-router-dom"
import { ChargePointFilter, ChargePointStatus } from "./types"
import * as api from "./api"
import { CBQueryParams } from "common/hooks/query-builder"

export const useStatus = () => {
  const matchStatus = useMatch("/org/:entity/charge-points/list/:status")

  const status =
    (matchStatus?.params?.status?.toUpperCase() as ChargePointStatus) ||
    ChargePointStatus.Pending

  return status
}

export const useStatusLabels = () => {
  const { t } = useTranslation()
  const statuses = useMemo(
    () => ({
      [ChargePointStatus.Pending]: t("En attente"),
      [ChargePointStatus.AuditInProgress]: t("En cours d'audit"),
      [ChargePointStatus.Accepted]: t("Accepté"),
    }),
    [t]
  )

  return statuses
}

const useArticle2Options = () => {
  const { t } = useTranslation()

  return useMemo(
    () => [
      {
        label: t("Concerné"),
        value: false,
      },
      {
        label: t("Pas concerné"),
        value: true,
      },
    ],
    [t]
  )
}

/**
 * Prepare the data for all filters
 * @param query
 * @returns Function
 */
export const useGetFilterOptions = (query: CBQueryParams) => {
  const { t } = useTranslation()
  const article2Options = useArticle2Options()
  const loadOptions = <T>(data: T) => new Promise<T>((resolve) => resolve(data))

  const getFilterOptions: FilterMultiSelectProps["getFilterOptions"] = async (
    filter
  ) => {
    const data = await api.getChargePointsFilters(filter, query)

    if (filter === ChargePointFilter.ConcernedByReadingMeter) {
      const transformedData = article2Options.filter(({ value }) =>
        data.includes(value)
      )
      return loadOptions(transformedData)
    }

    if (filter === ChargePointFilter.MeasureDate) {
      // Measure date can be null, so we have to translate this specific case
      const transformedData = data.map((value) =>
        value === "null"
          ? { label: t("Inconnu"), value }
          : { label: value, value }
      )

      return loadOptions(transformedData)
    }
    return loadOptions(data)
  }

  return getFilterOptions
}
