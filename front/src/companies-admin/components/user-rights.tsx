import { RightStatus } from "account/components/access-rights"
import { Alert } from "common/components/alert"
import { Confirm } from "common/components/dialog"
import { AlertCircle, Check, Cross } from "common/components/icons"
import { Input } from "common/components/input"
import Table, { actionColumn, Cell } from "common/components/table"
import { useQuery, useMutation } from "common/hooks/async"
import { UserRightRequest, UserRightStatus, UserRole } from "carbure/types"
import { useState } from "react"
import { useParams } from "react-router-dom"
import * as api from "../api"
import { Panel } from "common/components/scaffold"
import { usePortal } from "common/components/portal"
import { useTranslation } from "react-i18next"
import Button from "common/components/button"
import { compact } from "common/utils/collection"
import { formatDate } from "common/utils/formatters"
import useEntity from "carbure/hooks/entity"
import Select from "common/components/select"

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
  const entity = useEntity()
  const company_id = parseInt(id ?? "", 10)

  const [query, setQuery] = useState("")

  const rights = useQuery(api.getUsersRightRequests, {
    key: "user-right-requests",
    params: [entity.id, query, company_id],
  })

  const updateRight = useMutation(api.updateUsersRights, {
    invalidates: ["user-right-requests"],
  })

  const updateRole = useMutation(api.updateUserRole, {
    invalidates: ["user-right-requests"],
  })

  async function updateRightRequest(rightId: number, status: UserRightStatus) {
    portal((close) => (
      <Confirm
        title={t("Modifier droits d'accès")}
        description={t(`Voulez vous changer les droits d'accès de cet utilisateur en: {{status}} ?`, { status })} // prettier-ignore
        confirm={t("Confirmer")}
        variant="primary"
        onClose={close}
        onConfirm={async () => updateRight.execute(rightId, entity.id, status)}
      />
    ))
  }

  async function updateUserRole(rightId: number, role: UserRole) {
    portal((close) => (
      <Confirm
        title={t("Modifier le rôle")}
        description={t(`Voulez vous changer le rôle de cet utilisateur en "{{role}}" ?`, { role: ROLE_LABELS[role] })} // prettier-ignore
        confirm={t("Confirmer")}
        variant="primary"
        onClose={close}
        onConfirm={async () => updateRole.execute(rightId, entity.id, role)}
      />
    ))
  }

  const rows = rights.result?.data.data ?? []

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
          <Alert icon={AlertCircle} variant="warning">
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
              small: true,
              key: "status",
              header: "Statut",
              orderBy: (r) => RIGHTS_ORDER[r.status],
              cell: (r: UserRightRequest) => <RightStatus status={r.status} />,
            },
            {
              key: "user",
              header: "Utilisateur",
              orderBy: (r) => r.user[0] ?? "",
              cell: (r) => <Cell text={r.user[0] ?? ""} />,
            },
            {
              small: true,
              key: "role",
              header: "Droits",
              orderBy: (r) => ROLE_LABELS[r.role],
              cell: (r) => (
                <Select
                  variant="text"
                  value={r.role}
                  style={{ width: "180px" }}
                  options={Object.keys(ROLE_LABELS) as UserRole[]}
                  normalize={(role) => ({ value: role, label: ROLE_LABELS[role] })} // prettier-ignore
                  onChange={(role) => updateUserRole(r.id, role!)}
                />
              ),
            },
            {
              small: true,
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

      {rows.length === 0 && <footer />}
    </Panel>
  )
}

export default UserRights
