import { useMemo } from "react"
import useEntity from "common/hooks/entity"
import { useUser } from "common/hooks/user"
import {
  AccountingPermissions,
  getAccountingPermissions,
} from "accounting/permissions"

export type AccountingPermissionsManager = AccountingPermissions

export const useAccountingPermissions = (): AccountingPermissionsManager => {
  const user = useUser()
  const entity = useEntity()

  return useMemo(
    () => getAccountingPermissions(entity, user.isAuthenticated()),
    [entity, user]
  )
}
