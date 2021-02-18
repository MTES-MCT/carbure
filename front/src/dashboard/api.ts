import api from "common/services/api"
import { Declaration, Entity } from "common/types"

export type Entities = Record<number, Entity>
export type DeclarationsByMonth = Record<string, Declaration>
export type DeclarationsByEntities = Record<number, DeclarationsByMonth>

function groupDeclarationsByEntities(
  declarations: Declaration[]
): [Entity[], string[], DeclarationsByEntities] {
  const entities: Entities = {}
  const months: Record<string, null> = {}
  const declarationsByEntities: DeclarationsByEntities = {}

  declarations.forEach((declaration) => {
    const { entity, month, year } = declaration

    entities[entity.id] = entity
    const period = `${year}/${("0" + month).slice(-2)}`
    months[period] = null

    if (!declarationsByEntities[entity.id]) {
      declarationsByEntities[entity.id] = {}
    }

    declarationsByEntities[entity.id][period] = declaration
  })

  return [
    Object.values(entities),
    Object.keys(months).sort(),
    declarationsByEntities,
  ]
}

export function getDeclarations(): Promise<
  [Entity[], string[], DeclarationsByEntities]
> {
  return api
    .get("/admin/dashboard/declarations")
    .then(groupDeclarationsByEntities)
}

export function checkDeclaration(id: number): Promise<any> {
  return api.post("/admin/dashboard/declaration/check", { id })
}

export function uncheckDeclaration(id: number): Promise<any> {
  return api.post("/admin/dashboard/declaration/uncheck", { id })
}

export function sendDeclarationReminder(
  entity_id: number,
  year: number,
  month: number
): Promise<any> {
  return api.post("/admin/dashboard/declaration/send-reminder", {
    entity_id,
    year,
    month,
  })
}
