import { HttpResponse } from "msw"
import {
  currentAnnualDeclaration,
  currentAnnualDeclarationMissingFields,
} from "./data"
import { http } from "common/__test__/http"
import { AnnualDeclaration } from "biomethane/types"

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
