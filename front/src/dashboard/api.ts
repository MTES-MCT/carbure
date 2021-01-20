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
    const period = `${month}/${year}`
    months[period] = null

    if (!declarationsByEntities[entity.id]) {
      declarationsByEntities[entity.id] = {}
    }

    if (Object.values(declaration.lots).some((n) => n > 0)) {
      declarationsByEntities[entity.id][period] = declaration
    }
  })

  return [Object.values(entities), Object.keys(months), declarationsByEntities]
}

export function getDeclarations(): Promise<
  [Entity[], string[], DeclarationsByEntities]
> {
  return api
    .get("/admin/dashboard/declarations")
    .then(groupDeclarationsByEntities)
}
