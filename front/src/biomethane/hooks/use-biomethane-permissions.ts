import { useMemo } from "react"
import useEntity from "common/hooks/entity"
import { useUser } from "common/hooks/user"
import { ExternalAdminPages } from "common/types"

export const BIOMETHANE_PERMISSIONS = {
  CONTRACT: "biomethane.contract",
} as const

export type BiomethanePermissionKey =
  (typeof BIOMETHANE_PERMISSIONS)[keyof typeof BIOMETHANE_PERMISSIONS]

export interface BiomethanePermissionsManager {
  canAccessAdmin: boolean
  canAccessContract: boolean
  canAccessInjection: boolean
  canAccessModule: boolean

  // Can edit the declaration if the entity has write rights and is a DREAL
  canEditDeclaration: boolean
}

export const useBiomethanePermissions = (): BiomethanePermissionsManager => {
  const user = useUser()
  const entity = useEntity()

  const permissions = useMemo(() => {
    if (!user.isAuthenticated())
      return {
        canAccessAdmin: false,
        canAccessContract: false,
        canAccessInjection: false,
        canAccessModule: false,
        canEditDeclaration: false,
      }
    const canAccessAdmin = entity.hasAnyAdminRight([
      ExternalAdminPages.DREAL,
      ExternalAdminPages.ADEME,
    ])

    return {
      canAccessAdmin,
      canAccessContract: entity.hasAdminRight(ExternalAdminPages.DREAL),
      canAccessInjection: entity.hasAdminRight(ExternalAdminPages.DREAL),
      canEditDeclaration:
        entity.canWrite() && entity.hasAdminRight(ExternalAdminPages.DREAL),
      canAccessModule: entity.isBiomethaneProducer || canAccessAdmin,
    }
  }, [entity, user])

  return permissions
}
