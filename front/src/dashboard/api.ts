import api from "common/services/api"
import { Declaration, Entity, EntityType } from "common/types"

export type Entities = Record<number, Entity>
export type DeclarationsByMonth = { [k: string]: Declaration }
export type DeclarationsByEntities = { [k: number]: DeclarationsByMonth }
export type DeclarationsByEntityType = { [k: string]: DeclarationsByEntities }

function groupDeclarationsByEntities(
  declarations: Declaration[]
): [Entity[], string[], DeclarationsByEntityType] {
  const entities: Entities = {}
  const months: Record<string, null> = {}

  const declarationsByEntities: DeclarationsByEntityType = {
    [EntityType.Producer]: {},
    [EntityType.Trader]: {},
    [EntityType.Operator]: {},
  }

  declarations.forEach((declaration) => {
    const { entity, month, year } = declaration

    entities[entity.id] = entity
    const period = `${year}/${("0" + month).slice(-2)}`
    months[period] = null

    if (!declarationsByEntities[entity.entity_type][entity.id]) {
      declarationsByEntities[entity.entity_type][entity.id] = {}
    }

    declarationsByEntities[entity.entity_type][entity.id][period] = declaration
  })

  return [
    Object.values(entities),
    Object.keys(months).sort(),
    declarationsByEntities,
  ]
}

export function getDeclarations(): Promise<
  [Entity[], string[], DeclarationsByEntityType]
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
