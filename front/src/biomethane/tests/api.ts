import { http, HttpResponse } from "msw"
import { currentAnnualDeclaration } from "./data"

export const getCurrentAnnualDeclarationOk = http.get(
  "/api/biomethane/annual-declaration/",
  () => HttpResponse.json(currentAnnualDeclaration)
)
