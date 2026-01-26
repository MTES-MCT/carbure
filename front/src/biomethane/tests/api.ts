import { HttpResponse } from "msw"
import { annualDeclaration, annualDeclarationMissingFields } from "./data"
import { http } from "common/__test__/http"
import { AnnualDeclaration } from "biomethane/types"

export const getAnnualDeclarationYearsOk = http.get(
  "/biomethane/annual-declaration/years/",
  () => HttpResponse.json([2024, 2025])
)

export const getAnnualDeclarationOk = http.get(
  "/biomethane/annual-declaration/",
  () => HttpResponse.json(annualDeclaration)
)

export const getAnnualDeclarationMissingFields = http.get(
  "/biomethane/annual-declaration/",
  () => HttpResponse.json(annualDeclarationMissingFields)
)

export const buildAnnualDeclarationHandler = (
  declaration: Partial<AnnualDeclaration>
) =>
  http.get("/biomethane/annual-declaration/", () =>
    HttpResponse.json<AnnualDeclaration>({
      ...annualDeclaration,
      ...declaration,
    })
  )
