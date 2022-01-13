import { comparePeriod, prettyPeriod, Period } from "common/hooks/use-period"
import { Entity, EntityType } from "carbure/types"
import { Declaration } from "transactions/types"

export type Entities = Record<number, Entity>
export type DeclarationsByMonth = { [k: string]: Declaration }
export type DeclarationsByEntities = { [k: number]: DeclarationsByMonth }
export type DeclarationsByEntityType = { [k: string]: DeclarationsByEntities }

const CHECKED_ENTITIES = [
  EntityType.Producer,
  EntityType.Trader,
  EntityType.Operator,
]

export function groupDeclarationsByEntities(
  declarations: Declaration[]
): [Entity[], string[], DeclarationsByEntityType] {
  const entitiesMap: Entities = {}
  const monthsMap: Record<string, Period> = {}

  const byEntities: DeclarationsByEntityType = {
    [EntityType.Producer]: {},
    [EntityType.Trader]: {},
    [EntityType.Operator]: {},
  }

  declarations
    .filter((d) => CHECKED_ENTITIES.includes(d.entity.entity_type))
    .forEach((declaration) => {
      const { entity } = declaration
      const period = prettyPeriod(declaration)

      entitiesMap[entity.id] = entity
      monthsMap[period] = { year: declaration.year, month: declaration.month }

      if (!byEntities[entity.entity_type][entity.id]) {
        byEntities[entity.entity_type][entity.id] = {}
      }

      byEntities[entity.entity_type][entity.id][period] = declaration
    })

  const entities = Object.values(entitiesMap)
  const months = Object.values(monthsMap).sort(comparePeriod).map(prettyPeriod)

  return [entities, months, byEntities]
}
