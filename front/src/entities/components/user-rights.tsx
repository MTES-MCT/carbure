import { RightStatus } from "account/components/access-rights"
import { Alert } from "common/components/alert"
import { confirm } from "common/components/dialog"
import { AlertCircle, Check, Cross } from "common-v2/components/icons"
import { Input } from "common/components/input"
import Table, { Actions, Column, padding } from "common/components/table"
import useAPI from "common/hooks/use-api"
import { UserRightRequest, UserRightStatus, UserRole } from "carbure/types"
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { formatDate } from "settings/components/common"
import * as api from "../api"
import styles from "./user-rights.module.css"
import { Panel } from "common-v2/components/scaffold"

const ROLE_LABELS = {
  [UserRole.ReadOnly]: "Lecture seule",
  [UserRole.ReadWrite]: "Lecture/écriture",
  [UserRole.Admin]: "Administration",
  [UserRole.Auditor]: "Audit",
}

const RIGHTS_ORDER = {
  [UserRightStatus.Pending]: 0,
  [UserRightStatus.Accepted]: 1,
  [UserRightStatus.Revoked]: 2,
  [UserRightStatus.Rejected]: 3,
}

const RIGHTS_COLUMNS: Column<UserRightRequest>[] = [
  padding,
  {
    header: "Statut",
    render: (r: UserRightRequest) => <RightStatus status={r.status} />,
  },
  {
    header: "Utilisateur",
    render: (r) => r.user[0] ?? "",
  },
  {
    header: "Droits",
    render: (r) => ROLE_LABELS[r.role],
  },
  {
    header: "Date",
    render: (r) => {
      const dateRequested = formatDate(r.date_requested)
      const dateExpired = r.expiration_date ? formatDate(r.expiration_date) : null // prettier-ignore

      return dateExpired
        ? `${dateRequested} (expire le ${dateExpired})`
        : dateRequested
    },
  },
]

const UserRights = () => {
  const { id } = useParams<"id">()
  const [query, setQuery] = useState("")
  const [rights, getRights] = useAPI(api.getUsersRightRequests)

  const entityID = parseInt(id ?? "", 10)
  const [, updateRight] = useAPI(api.updateUsersRights)

  async function updateRightRequest(user: number, status: UserRightStatus) {
    const ok = await confirm(
      "Modifier droits d'accès",
      `Voulez vous changer les droits d'accès de cet utilisateur en: ${status} ?`
    )

    if (ok && entityID >= 0) {
      await updateRight(user, status)
      await getRights(query, entityID)
    }
  }

  useEffect(() => {
    getRights(query, entityID)
  }, [getRights, query, entityID])

  const rows = (rights.data ?? [])
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
            action: (r) => updateRightRequest(r.id, UserRightStatus.Revoked),
          },
        ]

      case UserRightStatus.Pending:
      case UserRightStatus.Rejected:
      case UserRightStatus.Revoked:
        return [
          {
            title: "Accepter",
            icon: Check,
            action: (r) => updateRightRequest(r.id, UserRightStatus.Accepted),
          },
          {
            title: "Refuser",
            icon: Cross,
            action: (r) => updateRightRequest(r.id, UserRightStatus.Rejected),
          },
        ]

      default:
        return []
    }
  })

  return (
    <Panel id="users">
      <header>
        <h1>Utilisateurs</h1>
      </header>

      <section>
        {(query.length > 0 || rows.length > 0) && (
          <Input
            placeholder="Rechercher utilisateur..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        )}
        {rows.length === 0 && (
          <Alert
            icon={AlertCircle}
            level="warning"
            className={styles.emptyUserRights}
          >
            Aucun utilisateur associé à cette entité
          </Alert>
        )}
      </section>

      {rows.length > 0 && (
        <Table columns={[...RIGHTS_COLUMNS, actions]} rows={rows} />
      )}
    </Panel>
  )
}

export default UserRights
