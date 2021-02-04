import { statusColumn } from "account/components/access-rights"
import { Title } from "common/components"
import { Alert } from "common/components/alert"
import { confirm } from "common/components/dialog"
import { AlertCircle, Check, Cross } from "common/components/icons"
import { Input } from "common/components/input"
import { Section, SectionBody, SectionHeader } from "common/components/section"
import Table, { Actions, Column } from "common/components/table"
import useAPI from "common/hooks/use-api"
import { UserRightRequest, UserRightStatus } from "common/types"
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { formatDate } from "settings/components/common"
import { padding } from "transactions/components/list-columns"
import * as api from "../api"
import styles from "./user-rights.module.css"

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
    header: "Date",
    render: (r) => formatDate(r.date_requested),
  },
]

const UserRights = () => {
  const { id } = useParams<{ id: string }>()
  const [query, setQuery] = useState("")
  const [rights, getRights] = useAPI(api.getUsersRightRequests)

  const entityID = parseInt(id, 10)
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
    <Section id="users">
      <SectionHeader>
        <Title>Utilisateurs</Title>
      </SectionHeader>

      <SectionBody>
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
      </SectionBody>

      {rows.length > 0 && (
        <Table columns={[...RIGHTS_COLUMNS, actions]} rows={rows} />
      )}
    </Section>
  )
}

export default UserRights
