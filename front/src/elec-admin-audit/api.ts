import { api, Api } from "common/services/api"

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/elec/admin/audit/years", {
    params: { entity_id },
  })
}
