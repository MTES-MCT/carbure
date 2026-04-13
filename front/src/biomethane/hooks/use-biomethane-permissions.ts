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
}

export const useBiomethanePermissions = (): BiomethanePermissionsManager => {
  const user = useUser()
  const entity = useEntity()

  const permissions = useMemo(() => {
    if (!user.isAuthenticated())
      return {
        canAccessAdmin: false,
        canAccessContract: false,
      }

    return {
      canAccessAdmin: entity.hasAnyAdminRight([
        ExternalAdminPages.DREAL,
        ExternalAdminPages.ADEME,
      ]),
      canAccessContract: entity.hasAdminRight(ExternalAdminPages.DREAL),
    }
  }, [entity, user])

  return permissions
}
