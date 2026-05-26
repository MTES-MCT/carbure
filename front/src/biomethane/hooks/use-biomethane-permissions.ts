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
  canAccessModule: boolean

  // Can edit the declaration if the entity has write rights and is a DREAL
  canEditDeclaration: boolean

  adminPermissions: {
    canAccessAdmin: boolean
    // Can access the supply plan admin endpoint if the entity has ADEME rights
    canAccessSupplyPlan: boolean
    canAccessContract: boolean
    canAccessInjection: boolean
    canDownloadDeclaration: boolean
  }
}

export const useBiomethanePermissions = (): BiomethanePermissionsManager => {
  const user = useUser()
  const entity = useEntity()

  const isDreal = entity.hasAnyAdminRight([ExternalAdminPages.DREAL])

  const permissions = useMemo(() => {
    if (!user.isAuthenticated())
      return {
        canAccessModule: false,
        canEditDeclaration: false,
        adminPermissions: {
          canAccessAdmin: false,
          canAccessSupplyPlan: false,
          canAccessContract: false,
          canAccessInjection: false,
          canDownloadDeclaration: false,
        },
      }
    const canAccessAdmin = entity.hasAnyAdminRight([
      ExternalAdminPages.DREAL,
      ExternalAdminPages.ADEME,
    ])

    return {
      canAccessModule: entity.isBiomethaneProducer || canAccessAdmin,
      canEditDeclaration: entity.canWrite() && isDreal,
      adminPermissions: {
        canAccessAdmin: canAccessAdmin,
        canAccessSupplyPlan: isDreal,
        canAccessContract: isDreal,
        canAccessInjection: isDreal,
        canDownloadDeclaration: isDreal,
      },
    }
  }, [entity, user, isDreal])

  return permissions
}
