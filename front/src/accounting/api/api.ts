import { api } from "common/services/api-fetch"

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
