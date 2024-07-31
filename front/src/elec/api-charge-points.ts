import { api, Api } from "common/services/api"

export function getYears(entity_id: number) {
  return api.get<Api<number[]>>("/elec/charge-points/years", {
    params: { entity_id },
  })
}
