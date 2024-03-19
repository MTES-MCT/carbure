import api from "common/services/api"
import { CompanyResult } from "./types"

// export async function searchCompanyData(siren: string) {
//   console.log('searchsiren:', siren)
//   const response = await api.get<{ results: CompanyResult[] }>("https://recherche-entreprises.api.gouv.fr/search", {
//     params: { q: siren },
//   })

//   console.log('response.data.results:', response.data.results)
//   return response.data.results

// }



export function getCompanyDataBySiren(
  entity_id: number,
  siren: string
) {
  return api.post<CompanyResult>("/entity/search-company", {
    entity_id,
    siren
  })
}
