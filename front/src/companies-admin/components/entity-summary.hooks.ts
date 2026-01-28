import { EntityType } from "common/types"
import { useCallback, useMemo } from "react"
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

  const updateFilter = useCallback(
    (filter: EntitySummaryFilter, value: string | string[] | undefined) => {
      setFiltersParams((prev) => {
        const newParams = new URLSearchParams(prev)

        // Supprimer toutes les valeurs existantes pour ce filtre
        newParams.delete(filter)

        if (value !== undefined && value !== "") {
          if (Array.isArray(value)) {
            value.forEach((v) => newParams.append(filter, v))
          } else {
            newParams.set(filter, value)
          }
        }

        return newParams
      })
    },
    [setFiltersParams]
  )

  const handleTypesChange = useCallback(
    (types: EntityType[] | undefined) => {
      updateFilter(EntitySummaryFilter.Types, types)
    },
    [updateFilter]
  )

  const handleOperationChange = useCallback(
    (operation: Operation | undefined) => {
      updateFilter(EntitySummaryFilter.Operation, operation)
    },
    [updateFilter]
  )

  const handleSearchChange = useCallback(
    (search: string | undefined) => {
      updateFilter(EntitySummaryFilter.Search, search)
    },
    [updateFilter]
  )

  return {
    filters,
    handleTypesChange,
    handleOperationChange,
    handleSearchChange,
  } as const
}
