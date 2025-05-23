import { useQuery, useMutation } from "common/hooks/async"
import { UserRightStatus } from "common/types"
import { useParams } from "react-router-dom"
import * as api from "../api"
import useEntity from "common/hooks/entity"
import { UserRightsTable } from "common/molecules/user-rights-table"

type UserRightsProps = {
  readOnly?: boolean
}

const UserRights = ({ readOnly }: UserRightsProps) => {
  const { id } = useParams<"id">()
  const entity = useEntity()
  const company_id = parseInt(id ?? "", 10)

  const response = useQuery(api.getUsersRightRequests, {
    key: "user-right-requests",
    params: [entity.id, "", company_id],
  })

  const updateRight = useMutation(api.updateUsersRights, {
    invalidates: ["user-right-requests"],
  })

  const updateRole = useMutation(api.updateUserRole, {
    invalidates: ["user-right-requests"],
  })

  const rights = response.result?.data ?? []

  return (
    <UserRightsTable
      readOnly={readOnly}
      rights={rights}
      onChangeUserRole={(role, right) =>
        updateRole.execute(right.id, entity.id, role)
      }
      onAcceptUser={(right) =>
        updateRight.execute(right.id, entity.id, UserRightStatus.Accepted)
      }
      onRevokeUser={(right) =>
        updateRight.execute(right.id, entity.id, UserRightStatus.Revoked)
      }
      onRejectUser={(right) =>
        updateRight.execute(right.id, entity.id, UserRightStatus.Rejected)
      }
      isSearchable
      onInputChange={(value) => response.execute(entity.id, value, company_id)}
    />
  )
}

export default UserRights
