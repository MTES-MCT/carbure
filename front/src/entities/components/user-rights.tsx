import { RightStatus } from "account/components/access-rights"
import { Alert } from "common-v2/components/alert"
import { Confirm } from "common-v2/components/dialog"
import { AlertCircle, Check, Cross } from "common-v2/components/icons"
import { Input } from "common-v2/components/input"
import Table, { actionColumn, Column } from "common-v2/components/table"
import { useQuery, useMutation } from "common-v2/hooks/async"
import { UserRightRequest, UserRightStatus, UserRole } from "carbure/types"
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { formatDate } from "settings/components/common"
import * as api from "../api"
import styles from "./user-rights.module.css"
import { Panel } from "common-v2/components/scaffold"
import { usePortal } from "common-v2/components/portal"
import { useTranslation } from "react-i18next"
import Button from "common-v2/components/button"
import { compact } from "common-v2/utils/collection"

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

const UserRights = () => {
  const { t } = useTranslation()
  const portal = usePortal()

  const { id } = useParams<"id">()
  const entityID = parseInt(id ?? "", 10)

  const [query, setQuery] = useState("")

  const rights = useQuery(api.getUsersRightRequests, {
    key: "user-right-requests",
    params: [query, entityID],
  })

  const updateRight = useMutation(api.updateUsersRights, {
    invalidates: ["user-right-requests"],
  })

  async function updateRightRequest(user: number, status: UserRightStatus) {
    portal((close) => (
      <Confirm
        title={t("Modifier droits d'accès")}
        description={t(`Voulez vous changer les droits d'accès de cet utilisateur en: {{status}} ?`, { status })} // prettier-ignore
        confirm={t("Confirmer")}
        variant="primary"
        onClose={close}
        onConfirm={async () => updateRight.execute(user, status)}
      />
    ))
  }

  const rows = rights.result ?? []

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
            variant="warning"
            className={styles.emptyUserRights}
          >
            Aucun utilisateur associé à cette entité
          </Alert>
        )}
      </section>

      {rows.length > 0 && (
        <Table
          order={{ column: "status", direction: "asc" }}
          rows={rows}
          columns={[
            {
              key: "status",
              header: "Statut",
              orderBy: (r) => RIGHTS_ORDER[r.status],
              cell: (r: UserRightRequest) => <RightStatus status={r.status} />,
            },
            {
              key: "user",
              header: "Utilisateur",
              orderBy: (r) => r.user[0] ?? "",
              cell: (r) => r.user[0] ?? "",
            },
            {
              key: "role",
              header: "Droits",
              orderBy: (r) => ROLE_LABELS[r.role],
              cell: (r) => ROLE_LABELS[r.role],
            },
            {
              key: "date",
              header: "Date",
              orderBy: (r) => r.date_requested,
              cell: (r) => {
                const dateRequested = formatDate(r.date_requested)
                const dateExpired = r.expiration_date ? formatDate(r.expiration_date) : null // prettier-ignore

                return dateExpired
                  ? `${dateRequested} (expire le ${dateExpired})`
                  : dateRequested
              },
            },
            actionColumn<UserRightRequest>((right) =>
              compact([
                right.status === UserRightStatus.Accepted && (
                  <Button
                    variant="icon"
                    title={t("Révoqer")}
                    icon={Cross}
                    action={() =>
                      updateRightRequest(right.id, UserRightStatus.Revoked)
                    }
                  />
                ),
                right.status !== UserRightStatus.Accepted && (
                  <Button
                    variant="icon"
                    title={t("Accepter")}
                    icon={Check}
                    action={() =>
                      updateRightRequest(right.id, UserRightStatus.Accepted)
                    }
                  />
                ),
                right.status !== UserRightStatus.Accepted && (
                  <Button
                    variant="icon"
                    title={t("Refuser")}
                    icon={Cross}
                    action={() =>
                      updateRightRequest(right.id, UserRightStatus.Rejected)
                    }
                  />
                ),
              ])
            ),
          ]}
        />
      )}
    </Panel>
  )
}

export default UserRights
