import { HttpResponse } from "msw"
import {
  currentAnnualDeclaration,
  currentAnnualDeclarationMissingFields,
} from "./data"
import { http } from "common/__test__/http"

export const getCurrentAnnualDeclarationOk = http.get(
  "/biomethane/annual-declaration/",
  () => HttpResponse.json(currentAnnualDeclaration)
)

export const getCurrentAnnualDeclarationMissingFields = http.get(
  "/biomethane/annual-declaration/",
  () => HttpResponse.json(currentAnnualDeclarationMissingFields)
)

export const buildCurrentAnnualDeclarationHandler = (missingFields: {
  digestate_missing_fields: string[]
  energy_missing_fields: string[]
}) =>
  http.get("/biomethane/annual-declaration/", () =>
    HttpResponse.json({
      ...currentAnnualDeclaration,
      missing_fields: missingFields,
    })
  )
