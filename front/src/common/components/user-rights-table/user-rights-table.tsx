import { Trans, useTranslation } from "react-i18next"
import { RightStatus } from "account/components/access-rights"
import { Alert } from "common/components/alert"
import { AlertCircle } from "common/components/icons"
import Table, { actionColumn, Cell } from "common/components/table"
import { UserRightRequest, UserRightStatus } from "carbure/types"
import { getUserRoleLabel } from "carbure/utils/normalizers"
import { Panel } from "common/components/scaffold"
import { compact } from "common/utils/collection"
import { formatDate } from "common/utils/formatters"
import { EditUserRightsButton } from "./edit-user-rights-button"
import { AcceptUserButton } from "./accept-user-button"
import { RevokeUserButton } from "./revoke-user-button"

type EntityUserRightsProps = {
  rights: UserRightRequest[]

  // Loading state during user right edition mutation
  isLoadingEditUserRight: boolean

  // Function called when the role of an user is changed
  onEditUserRight: () => void

  // Function called when a user is accepted
  onAcceptUser: () => void

  // Function called when a user is revoked
  onRevokeUser: () => void
}

const RIGHTS_ORDER = {
  [UserRightStatus.Pending]: 0,
  [UserRightStatus.Accepted]: 1,
  [UserRightStatus.Revoked]: 2,
  [UserRightStatus.Rejected]: 3,
}

export const UserRightsTable = ({
  rights,
  isLoadingEditUserRight,
  onEditUserRight,
  onAcceptUser,
  onRevokeUser,
}: EntityUserRightsProps) => {
  const { t } = useTranslation()

  return (
    <Panel id="users">
      <header>
        <h1>
          <Trans>Generic Utilisateurs</Trans>
        </h1>
      </header>

      {rights.length === 0 && (
        <>
          <section>
            <Alert icon={AlertCircle} variant="warning">
              <Trans>Aucun utilisateur associé à cette entité</Trans>
            </Alert>
          </section>
          <footer />
        </>
      )}

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
                  <EditUserRightsButton
                    request={request}
                    loading={isLoadingEditUserRight}
                    onEditUserRight={onEditUserRight}
                  />
                ),
                request.status !== UserRightStatus.Accepted && (
                  <AcceptUserButton
                    onAcceptUser={onAcceptUser}
                    request={request}
                  />
                ),
                request.status !== UserRightStatus.Accepted && (
                  <div>REJECT</div>
                ),
                request.status === UserRightStatus.Accepted && (
                  <RevokeUserButton
                    onRevokeUser={onRevokeUser}
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
