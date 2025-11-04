import { http } from "common/__test__/http"
import { HttpResponse } from "msw"
import { BiomethaneProductionUnit } from "../types"
import { productionUnitData } from "./data"

export const getProductionUnitOk = http.get(
  "/biomethane/production-unit/",
  () => HttpResponse.json<BiomethaneProductionUnit>(productionUnitData)
)
