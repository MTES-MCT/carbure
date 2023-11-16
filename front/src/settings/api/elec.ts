import api, { Api } from "common/services/api"
import { elecChargingPointsApplications } from "elec/__test__/data"
import { ElecChargingPointsApplication } from "elec/types"



export function getChargingPointsApplications(entity_id: number) {

  // TO TEST without data
  return new Promise<ElecChargingPointsApplication[]>((resolve) => {
    resolve(elecChargingPointsApplications)
  })

  // return api.get<Api<ElecChargingPointsApplication[]>>("/v5/elec/charging-points-applications", {
  //   params: { entity_id },
  // })
}
