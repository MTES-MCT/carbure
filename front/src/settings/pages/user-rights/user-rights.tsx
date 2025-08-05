import useEntity from "common/hooks/entity"
import { UserRightsTable } from "common/molecules/user-rights-table"
import {
  useAcceptUserRights,
  useChangeUserRole,
  useGetEntityRights,
  useInviteUser,
  useRevokeUserRights,
} from "./user-rights.hooks"

export const EntityUserRights = () => {
  const entity = useEntity()

  const { rights } = useGetEntityRights()

  const changeUserRole = useChangeUserRole()

  const revokeRight = useRevokeUserRights()

  const acceptRight = useAcceptUserRights()

  const inviteUser = useInviteUser()

  return rights.map(({ title, description, data }) => (
    <UserRightsTable
      title={title}
      description={description}
      rights={data}
      onChangeUserRole={(role, request) =>
        changeUserRole.execute(entity.id, request.user[0] ?? "", role)
      }
      onAcceptUser={(request) => acceptRight.execute(entity.id, request.id)}
      onRevokeUser={(request) =>
        revokeRight.execute(entity.id, request.user[0] ?? "")
      }
      // Reject and revoke call the same endpoint, just UI is different
      onRejectUser={(request) =>
        revokeRight.execute(entity.id, request.user[0] ?? "")
      }
      onAddNewUser={(email, role) => inviteUser.execute(entity.id, email, role)}
    />
  ))
}
