import { statusColumn } from "account/components/access-rights"
import { Title } from "common/components"
import { Alert } from "common/components/alert"
import { confirm } from "common/components/dialog"
import { AlertCircle, Check, Cross } from "common/components/icons"
import { Section, SectionBody, SectionHeader } from "common/components/section"
import Table, { Actions, Column } from "common/components/table"
import useAPI from "common/hooks/use-api"
import { UserRightRequest, UserRightStatus, UserRole } from "common/types"
import { useEffect } from "react"
import { formatDate } from "settings/components/common"
import { padding } from "transactions/components/list-columns"
import * as api from "../api"
import styles from "entities/components/user-rights.module.css"
import colStyles from "transactions/components/list-columns.module.css"
import { EntitySelection } from "carbure/hooks/use-entity"

const ROLE_LABELS = {
  [UserRole.ReadOnly]: "Lecture seule",
  [UserRole.ReadWrite]: "Lecture/écriture",
  [UserRole.Admin]: "Administration",
  [UserRole.Auditor]: "Audit",
}

const STATUS_LABELS = {
  [UserRightStatus.Pending]: "En attente",
  [UserRightStatus.Accepted]: "Accepté",
  [UserRightStatus.Revoked]: "Révoqué",
  [UserRightStatus.Rejected]: "Refusé",
}

const RIGHTS_ORDER = {
  [UserRightStatus.Pending]: 0,
  [UserRightStatus.Accepted]: 1,
  [UserRightStatus.Revoked]: 2,
  [UserRightStatus.Rejected]: 3,
}

const RIGHTS_COLUMNS: Column<UserRightRequest>[] = [
  padding,
  statusColumn,
  {
    header: "Utilisateur",
    render: (r) => r.user[0] ?? "",
  },
  {
    header: "Droits",
    className: colStyles.narrowColumn,
    render: (r) => ROLE_LABELS[r.role],
  },
  {
    header: "Date",
    className: colStyles.narrowColumn,
    render: (r) => formatDate(r.date_requested),
  },
]

const UserRights = ({ entity }: { entity: EntitySelection }) => {
  const [rights, getRights] = useAPI(api.getEntityRights)
  // const [, updateRight] = useAPI(api.updateUsersRights)

  const entityID = entity?.id ?? -1

  async function updateRightRequest(
    request: UserRightRequest,
    status: UserRightStatus
  ) {
    const ok = await confirm(
      "Modifier droits d'accès",
      `Voulez vous changer les droits d'accès de l'utilisateur ${request.user} en "${STATUS_LABELS[status]}" ?`
    )

    if (ok && entityID >= 0) {
      // await updateRight(request.id, status)
      await getRights(entityID)
    }
  }

  useEffect(() => {
    getRights(entityID)
  }, [getRights, entityID])

  const rows = (rights.data?.requests ?? [])
    .map((r) => ({ value: r }))
    .sort((a, b) => RIGHTS_ORDER[a.value.status] - RIGHTS_ORDER[b.value.status])

  // available actions are different depending on the status of the user
  const actions = Actions<UserRightRequest>((right) => {
    switch (right.status) {
      case UserRightStatus.Accepted:
        return [
          {
            title: "Révoqer",
            icon: Cross,
            action: (r) => updateRightRequest(r, UserRightStatus.Revoked),
          },
        ]

      case UserRightStatus.Pending:
      case UserRightStatus.Rejected:
      case UserRightStatus.Revoked:
        return [
          {
            title: "Accepter",
            icon: Check,
            action: (r) => updateRightRequest(r, UserRightStatus.Accepted),
          },
          {
            title: "Refuser",
            icon: Cross,
            action: (r) => updateRightRequest(r, UserRightStatus.Rejected),
          },
        ]

      default:
        return []
    }
  })

  return (
    <Section id="users">
      <SectionHeader>
        <Title>Utilisateurs</Title>
      </SectionHeader>

      <SectionBody>
        {rows.length === 0 && (
          <Alert
            icon={AlertCircle}
            level="warning"
            className={styles.emptyUserRights}
          >
            Aucun utilisateur associé à cette entité
          </Alert>
        )}
      </SectionBody>

      {rows.length > 0 && (
        <Table columns={[...RIGHTS_COLUMNS, actions]} rows={rows} />
      )}
    </Section>
  )
}

export default UserRights
