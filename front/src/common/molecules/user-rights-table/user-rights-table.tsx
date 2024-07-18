import { Trans, useTranslation } from "react-i18next"
import { RightStatus } from "account/components/access-rights"
import { Alert } from "common/components/alert"
import { AlertCircle, Plus } from "common/components/icons"
import { SearchInput } from "common/components/input"
import { Button, MailTo } from "common/components/button"
import Table, { actionColumn, Cell } from "common/components/table"
import { usePortal } from "common/components/portal"
import { UserRightRequest, UserRightStatus, UserRole } from "carbure/types"
import { getUserRoleLabel } from "carbure/utils/normalizers"
import { Panel } from "common/components/scaffold"
import { compact } from "common/utils/collection"
import { formatDate } from "common/utils/formatters"
import { ChangeUserRoleButton } from "./change-user-role-button"
import { AcceptUserButton } from "./accept-user-button"
import { RevokeUserButton } from "./revoke-user-button"
import { RejectUserButton } from "./reject-user-button"
import { useState } from "react"
import { AddUserDialog } from "./add-user-dialog"

type EntityUserRightsProps = {
  rights: UserRightRequest[]

  // Function called when the role of an user is changed
  onChangeUserRole: (
    role: UserRole,
    request: UserRightRequest
  ) => Promise<unknown>

  // Function called when a user is accepted
  onAcceptUser: (request: UserRightRequest) => void

  // Function called when a user is revoked
  onRevokeUser: (request: UserRightRequest) => void

  // Function called when a user is rejected
  onRejectUser: (request: UserRightRequest) => void

  // Function called when the input value change
  onInputChange?: (value: string) => void

  // Allow search input
  isSearchable?: boolean
}

const RIGHTS_ORDER = {
  [UserRightStatus.Pending]: 0,
  [UserRightStatus.Accepted]: 1,
  [UserRightStatus.Revoked]: 2,
  [UserRightStatus.Rejected]: 3,
}

export const UserRightsTable = ({
  rights,
  isSearchable = false,
  onChangeUserRole,
  onAcceptUser,
  onRevokeUser,
  onRejectUser,
  onInputChange,
}: EntityUserRightsProps) => {
  const { t } = useTranslation()
  const [query, setQuery] = useState<string>("")
  const portal = usePortal()

  const displaySearchInput =
    isSearchable && (query.length > 0 || rights.length > 0)
  // Pass all the request as parameter to let the parent do anything
  const handleChangeUserRole =
    (request: UserRightRequest) => (role: UserRole) =>
      onChangeUserRole(role, request)

  const handleInputChange = (value: string | undefined) => {
    setQuery(value || "")
    onInputChange?.(value || "")
  }

  return (
    <Panel id="users">
      <header>
        <h1>
          <Trans>Utilisateurs</Trans>
        </h1>
        <Button
          asideX
          variant="primary"
          icon={Plus}
          label={t("Ajouter un utilisateur")}
          action={() => portal((close) => <AddUserDialog onClose={close} />)}
        />
      </header>

      <section>
        {displaySearchInput && (
          <SearchInput
            placeholder={t("Rechercher utilisateur...")}
            value={query}
            onChange={handleInputChange}
            debounce={300}
          />
        )}
        {rights.length === 0 && (
          <Alert icon={AlertCircle} variant="warning">
            <Trans>Aucun utilisateur associé à cette entité</Trans>
          </Alert>
        )}
      </section>

      {rights.length > 0 && (
        <Table
          order={{ column: "status", direction: "asc" }}
          rows={rights}
          columns={[
            {
              small: true,
              key: "status",
              header: "Statut",
              orderBy: (r) => RIGHTS_ORDER[r.status],
              cell: (r) => <RightStatus status={r.status} />,
            },
            {
              key: "user",
              header: t("Utilisateur"),
              orderBy: (r) => r.user[0] ?? "",
              cell: (r) => <Cell text={r.user[0] ?? ""} />,
            },
            {
              small: true,
              key: "role",
              header: t("Droits"),
              orderBy: (r) => getUserRoleLabel(r.role),
              cell: (r) => getUserRoleLabel(r.role),
            },
            {
              small: true,
              key: "date",
              header: t("Date"),
              orderBy: (r) => r.date_requested,
              cell: (r) => {
                const dateRequested = formatDate(r.date_requested)
                const dateExpired = r.expiration_date ? formatDate(r.expiration_date) : null // prettier-ignore

                return dateExpired
                  ? t("{{dateRequested}} (expire le {{dateExpired}})", { dateRequested, dateExpired }) // prettier-ignore
                  : dateRequested
              },
            },
            actionColumn<UserRightRequest>((request) =>
              compact([
                request.status === UserRightStatus.Accepted && (
                  <ChangeUserRoleButton
                    request={request}
                    onChangeUserRole={handleChangeUserRole(request)}
                  />
                ),
                request.status !== UserRightStatus.Accepted && (
                  <AcceptUserButton
                    onAcceptUser={() => onAcceptUser(request)}
                    request={request}
                  />
                ),
                request.status !== UserRightStatus.Accepted && (
                  <RejectUserButton
                    onRejectUser={() => onRejectUser(request)}
                    request={request}
                  />
                ),
                request.status === UserRightStatus.Accepted && (
                  <RevokeUserButton
                    onRevokeUser={() => onRevokeUser(request)}
                    request={request}
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
