import useEntity from "common/hooks/entity"
import { ExternalAdminPages } from "common/types"

export const useH2Permissions = () => {
  const entity = useEntity()

  const canAccessAdmin =
    entity.isExternal && entity.hasAdminRight(ExternalAdminPages.H2)

  const canWriteStations = entity.canWrite() && !canAccessAdmin

  return { canAccessAdmin, canWriteStations }
}
