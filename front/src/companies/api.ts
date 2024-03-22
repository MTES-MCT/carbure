import api, { Api } from "common/services/api"
import { SearchCompanyResult } from "./types"

// export async function searchCompanyData(siren: string) {
//   console.log('searchsiren:', siren)
//   const response = await api.get<{ results: SearchCompanyResult[] }>("https://recherche-entreprises.api.gouv.fr/search", {
//     params: { q: siren },
//   })

//   console.log('response.data.results:', response.data.results)
//   return response.data.results

// }



export function searchCompanyDataBySiren(
  registration_id: string
) {
  return api.post<Api<SearchCompanyResult>>("/entity/search-company", {
    registration_id
  })
}
