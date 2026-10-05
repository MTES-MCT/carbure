import { api, HttpError } from "common/services/api-fetch"
import { apiTypes } from "common/services/api-fetch.types"

// Annual declaration
export const getCurrentAnnualDeclaration = async (entity_id: number) => {
  return api.GET("/tiruert/declaration-period/", {
    params: {
      query: {
        entity_id,
      },
    },
  })
}

export const getDeclarationPeriodYears = async (entity_id: number) => {
  return api.GET("/tiruert/declaration-period/years/", {
    params: {
      query: {
        entity_id,
      },
    },
  })
}

export const getSnapshotBalance = async (
  entity_id: number,
  year: number,
  selected_entity_id?: number
): Promise<apiTypes["SnapshotBalance"] | undefined> => {
  try {
    const response = await api.GET("/tiruert/objectives/snapshot-balance/", {
      params: {
        query: {
          entity_id,
          year: `${year}`,
          ...(selected_entity_id !== undefined && { selected_entity_id }),
        },
      },
    })
    return response.data
  } catch (error) {
    if (error instanceof HttpError && error.status === 404) return undefined
    throw error
  }
}
