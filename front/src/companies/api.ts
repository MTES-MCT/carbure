import api, { Api } from "common/services/api"
import { AxiosResponse } from "axios"
import { CompanyResult } from "./types"

export async function searchCompanyData(siren: string) {
  console.log('siren:', siren)
  return await api.get<{ results: CompanyResult[] }>("https://recherche-entreprises.api.gouv.fr/search", {
    params: { q: siren },
  }).then((response: AxiosResponse<{ results: CompanyResult[] }>) => {
    return response.data.results
  })
}
