import { EntityType } from "common/types"
import { useMemo } from "react"
import { useSearchParams } from "react-router-dom"

export type Operation =
  | "authorize"
  | "user"
  | "certificate"
  | "double-counting"
  | "charge-points"
  | "meter-readings"

export enum EntitySummaryFilter {
  Types = "types",
  Operation = "operation",
  Search = "search",
}

const enumValues = Object.values(EntitySummaryFilter)

type EntitySummaryFilters = {
  [EntitySummaryFilter.Types]: EntityType[]
  [EntitySummaryFilter.Operation]?: Operation
  [EntitySummaryFilter.Search]: string
}

export const useEntitySummaryFilters = () => {
  const [filtersParams, setFiltersParams] = useSearchParams()

  const filters = useMemo(() => {
    const filters: EntitySummaryFilters = {
      [EntitySummaryFilter.Types]: [],
      [EntitySummaryFilter.Operation]: undefined,
      [EntitySummaryFilter.Search]: "",
    }

    filtersParams.forEach((value, filter) => {
      if (enumValues.includes(filter as EntitySummaryFilter)) {
        switch (filter) {
          case EntitySummaryFilter.Types:
            ;(filters[EntitySummaryFilter.Types] as EntityType[]).push(
              value as EntityType
            )
            break
          case EntitySummaryFilter.Operation:
            filters[EntitySummaryFilter.Operation] = value as Operation
            break
          case EntitySummaryFilter.Search:
            filters[EntitySummaryFilter.Search] = value
            break
        }
      }
    })
    return filters
  }, [filtersParams])

  return [filters, setFiltersParams] as const
}
