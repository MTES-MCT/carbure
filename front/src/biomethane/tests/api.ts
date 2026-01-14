import { HttpResponse } from "msw"
import {
  currentAnnualDeclaration,
  currentAnnualDeclarationMissingFields,
} from "./data"
import { http } from "common/__test__/http"
import { AnnualDeclaration } from "biomethane/types"

export const getAnnualDeclarationYearsOk = http.get(
  "/biomethane/annual-declaration/years/",
  () => HttpResponse.json([2024, 2025])
)

export const getCurrentAnnualDeclarationOk = http.get(
  "/biomethane/annual-declaration/",
  () => HttpResponse.json(currentAnnualDeclaration)
)

export const getCurrentAnnualDeclarationMissingFields = http.get(
  "/biomethane/annual-declaration/",
  () => HttpResponse.json(currentAnnualDeclarationMissingFields)
)

export const buildCurrentAnnualDeclarationHandler = (
  declaration: Partial<AnnualDeclaration>
) =>
  http.get("/biomethane/annual-declaration/", () =>
    HttpResponse.json<AnnualDeclaration>({
      ...currentAnnualDeclaration,
      ...declaration,
    })
  )
