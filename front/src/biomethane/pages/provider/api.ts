import { api } from "common/services/api-fetch"
import { BiomethaneProviderDeclarationsQuery } from "./types"

export const getBiomethaneProviderDeclarations = (
  query: BiomethaneProviderDeclarationsQuery
) =>
  api
    .GET("/biomethane/provider/declarations/", {
      params: {
        query,
      },
    })
    .then((res) => res.data)
