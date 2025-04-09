import useEntity from "common/hooks/entity"
import { UserRole } from "common/types"

export const useSafRules = () => {
  const entity = useEntity()

  const canUpdateTicket =
    entity.hasRights(UserRole.ReadWrite) || entity.hasRights(UserRole.Admin)

  return { canUpdateTicket }
}
