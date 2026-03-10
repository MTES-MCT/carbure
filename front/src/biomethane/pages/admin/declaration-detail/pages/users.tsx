import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useSelectedEntity } from "common/providers/selected-entity-provider"
import { UserRightsTable } from "common/molecules/user-rights-table"
import { getUsersRightRequests } from "companies-admin/api"
import { useTranslation } from "react-i18next"

const Users = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { selectedEntityId } = useSelectedEntity()
  const { result: entityRightsResponse } = useQuery(getUsersRightRequests, {
    key: "entity-rights",
    params: [entity.id, "", selectedEntityId!],
  })

  const rights = entityRightsResponse?.data ?? []

  return (
    <UserRightsTable
      rights={rights}
      readOnly
      onChangeUserRole={() => Promise.resolve()}
      onAcceptUser={() => {}}
      onRevokeUser={() => {}}
      onRejectUser={() => {}}
      description={t(
        "Vous pouvez visualiser les utilisateurs de cette société ici."
      )}
    />
  )
}

export default Users
