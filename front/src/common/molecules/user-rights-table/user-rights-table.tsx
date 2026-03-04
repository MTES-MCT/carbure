import { useTranslation } from "react-i18next"
import { RightStatus } from "account/components/access-rights"
import { SearchInput } from "common/components/inputs2"
import { Button } from "common/components/button2"
import { actionColumn, Cell, Table } from "common/components/table2"
import { usePortal } from "common/components/portal"
import { UserRightRequest, UserRightStatus, UserRole } from "common/types"
import { getUserRoleLabel } from "common/utils/normalizers"
import { compact } from "common/utils/collection"
import { formatDate } from "common/utils/formatters"
import { ChangeUserRoleButton } from "./change-user-role-button"
import { AcceptUserButton } from "./accept-user-button"
import { RevokeUserButton } from "./revoke-user-button"
import { RejectUserButton } from "./reject-user-button"
import { useState } from "react"
import { AddUserDialog, AddUserDialogProps } from "./add-user-dialog"
import { EditableCard } from "../editable-card"
import { Notice } from "common/components/notice"

type EntityUserRightsProps = {
  // Overrides default user title
  title?: string

  // Overrides default user description
  description?: string

  rights: UserRightRequest[]

  readOnly?: boolean

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

  onAddNewUser?: AddUserDialogProps["onAddNewUser"]
}

const RIGHTS_ORDER = {
  [UserRightStatus.Pending]: 0,
  [UserRightStatus.Accepted]: 1,
  [UserRightStatus.Revoked]: 2,
  [UserRightStatus.Rejected]: 3,
}

export const UserRightsTable = ({
  title: overrideTitle,
  description: overrideDescription,
  rights,
  readOnly,
  isSearchable = false,
  onChangeUserRole,
  onAcceptUser,
  onRevokeUser,
  onRejectUser,
  onInputChange,
  onAddNewUser,
}: EntityUserRightsProps) => {
  const { t } = useTranslation()
  const [query, setQuery] = useState<string>("")
  const portal = usePortal()

  const title = overrideTitle ?? t("Utilisateurs")
  const description =
    overrideDescription ??
    t("Gérez les membres de votre équipe ici selon leurs droits.")

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
    <EditableCard
      title={title}
      description={description}
      headerActions={
        onAddNewUser ? (
          <Button
            asideX
            iconId="ri-add-line"
            onClick={() =>
              portal((close) => (
                <AddUserDialog onClose={close} onAddNewUser={onAddNewUser} />
              ))
            }
          >
            {t("Ajouter un utilisateur")}
          </Button>
        ) : null
      }
    >
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
          <Notice
            variant="warning"
            icon="ri-error-warning-line"
            title={t("Aucun utilisateur associé à cette entité")}
          />
        )}
      </section>

      {rights.length === 0 && <footer />}

      {rights.length > 0 && (
        <Table
          order={{ column: "status", direction: "asc" }}
          rows={rights}
          columns={compact([
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
              orderBy: (r) => r.user.email ?? "",
              cell: (r) => <Cell text={r.user.email ?? ""} />,
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
            !readOnly &&
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
          ])}
        />
      )}
    </EditableCard>
  )
}
