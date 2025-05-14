import { apiTypes } from "common/services/api-fetch.types"
import { OperationsFilter, OperationsQuery, OperationOrderBy } from "../types"
import { api, download } from "common/services/api-fetch"
import { formatOperation } from "accounting/utils/formatters"

export const getOperationsFilters = (
  filter: string,
  query: OperationsQuery
) => {
  return api.GET("/tiruert/operations/filters/", {
    params: {
      query: {
        ...query,
        filter: filter as OperationsFilter,
      },
    },
  })
}

export const getOperations = (query: OperationsQuery) => {
  return api
    .GET("/tiruert/operations/", {
      params: {
        query: {
          ...query,
          order_by:
            query.order_by && query.order_by.length > 0
              ? query.order_by
              : [OperationOrderBy.ValueMinuscreated_at],
        },
      },
    })
    .then((response) => ({
      ...response,
      data: {
        ...response.data,
        results: response.data?.results.map((operation) => ({
          ...operation,
          ...formatOperation(operation),
        })),
      },
    }))
}

export const patchOperation = (
  entityId: number,
  operationId: number,
  data: apiTypes["PatchedOperationUpdateRequest"]
) => {
  return api.PATCH("/tiruert/operations/{id}/", {
    params: {
      query: {
        entity_id: entityId,
      },
      path: {
        id: operationId,
      },
    },
    body: data,
  })
}

export const simulateMinMax = (
  entityId: number,
  {
    biofuel,
    customs_category,
    debited_entity,
    target_volume,
    unit,
    from_depot,
    ges_bound_min,
    ges_bound_max,
  }: apiTypes["SimulationInputRequest"]
) => {
  return api.POST("/tiruert/operations/simulate/min_max/", {
    params: { query: { entity_id: entityId } },
    body: {
      biofuel,
      customs_category,
      debited_entity,
      target_volume,
      unit,
      from_depot,
      ges_bound_min,
      ges_bound_max,
    },
  })
}

// Get the lots that can be used to create an operation
export const simulate = (
  entityId: number,
  data: apiTypes["SimulationInputRequest"]
) => {
  return api.POST("/tiruert/operations/simulate/", {
    params: { query: { entity_id: entityId } },
    body: data,
  })
}

export const createOperation = (
  entityId: number,
  data: Omit<apiTypes["OperationInputRequest"], "lots"> & {
    lots: apiTypes["SimulationLotOutput"][]
  }
) => {
  return api.POST("/tiruert/operations/", {
    params: { query: { entity_id: entityId } },
    body: {
      ...data,
      lots: data.lots.map(({ lot_id, ...rest }) => ({
        ...rest,
        volume: parseFloat(rest.volume),
        id: lot_id,
      })),
    },
    bodySerializer: (data) => JSON.stringify(data), // Body contains array of objects, our backend could not handle it in a formData
  })
}

/**
 * In the case of transfers and teneurs, we need to simulate the lots before creating the operation
 *
 */
export const createOperationWithSimulation = (
  entityId: number,
  {
    simulation,
    operation,
    customs_category,
    biofuel,
    debited_entity,
    from_depot,
  }: Pick<
    apiTypes["OperationInputRequest"],
    "customs_category" | "biofuel" | "debited_entity" | "from_depot"
  > & {
    simulation: Pick<
      apiTypes["SimulationInputRequest"],
      "target_volume" | "target_emission" | "unit"
    >
    operation: Pick<
      apiTypes["OperationInputRequest"],
      "type" | "from_depot" | "to_depot" | "credited_entity"
    >
  }
) => {
  return simulate(entityId, {
    customs_category,
    biofuel,
    debited_entity,
    target_emission: simulation.target_emission,
    target_volume: simulation.target_volume,
    unit: simulation.unit,
    from_depot,
  }).then((response) => {
    const lots = response.data?.selected_lots
    if (lots) {
      return createOperation(entityId, {
        ...operation,
        lots,
        biofuel,
        customs_category,
        debited_entity,
        type: operation.type,
        from_depot: operation.from_depot,
        to_depot: operation.to_depot,
        credited_entity: operation.credited_entity,
      })
    }
  })
}

export const getOperationDetail = (entity_id: number, id: number) => {
  return api
    .GET(`/tiruert/operations/{id}/`, {
      params: {
        query: {
          entity_id,
        },
        path: {
          id,
        },
      },
    })
    .then((response) => ({
      ...response,
      data: response.data
        ? {
            ...response.data,
            ...formatOperation(response.data),
          }
        : undefined,
    }))
}

export const deleteOperation = (entity_id: number, operation_id: number) => {
  return api.DELETE(`/tiruert/operations/{id}/`, {
    params: {
      query: {
        entity_id,
      },
      path: {
        id: operation_id,
      },
    },
  })
}

export const acceptOperation = (entity_id: number, operation_id: number) => {
  return api.POST(`/tiruert/operations/{id}/accept/`, {
    params: {
      query: {
        entity_id,
      },
      path: { id: operation_id },
    },
  })
}

export const rejectOperation = (entity_id: number, operation_id: number) => {
  return api.POST(`/tiruert/operations/{id}/reject/`, {
    params: {
      query: {
        entity_id,
      },
      path: { id: operation_id },
    },
  })
}

export function downloadOperations(query: OperationsQuery) {
  return download(`/tiruert/operations/export/`, {
    ...query,
  })
}
