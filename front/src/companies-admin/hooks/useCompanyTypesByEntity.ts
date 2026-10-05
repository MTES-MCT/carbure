import useEntity, { EntityManager } from "common/hooks/entity"
import { EntityType, ExternalAdminPages } from "common/types"

const ADMIN_TO_ENTITIES: Partial<Record<ExternalAdminPages, EntityType[]>> = {
  [ExternalAdminPages.DREAL]: [EntityType.Producteur_de_biom_thane],
  [ExternalAdminPages.ELEC]: [EntityType.Operator, EntityType.CPO],
  [ExternalAdminPages.H2]: [EntityType.HRS],
}

const ALL_ENTITIES = Object.values(EntityType)

const getCompanyTypesForAdmin = (entity: EntityManager) => {
  return Object.entries(ADMIN_TO_ENTITIES).reduce<EntityType[]>(
    (acc, [admin, entities]) => {
      if (entity.hasAdminRight(admin as ExternalAdminPages)) {
        return [...acc, ...entities]
      }
      return acc
    },
    []
  )
}

export const useCompanyTypesByEntity = () => {
  const entity = useEntity()
  return entity.isAdmin ? ALL_ENTITIES : getCompanyTypesForAdmin(entity)
}
