import { Trans, useTranslation } from "react-i18next"
import { RightStatus } from "account/components/access-rights"
import { Alert } from "common/components/alert"
import { AlertCircle } from "common/components/icons"
import Table, { actionColumn, Cell } from "common/components/table"
import { UserRightRequest, UserRightStatus } from "carbure/types"
import { getUserRoleLabel } from "carbure/utils/normalizers"
import { Panel } from "common/components/scaffold"
import useEntity from "carbure/hooks/entity"
import { compact } from "common/utils/collection"
import { formatDate } from "common/utils/formatters"

type EntityUserRightsProps = {
  rights: UserRightRequest[]
}

const RIGHTS_ORDER = {
  [UserRightStatus.Pending]: 0,
  [UserRightStatus.Accepted]: 1,
  [UserRightStatus.Revoked]: 2,
  [UserRightStatus.Rejected]: 3,
}

export const EntityUserRights = ({ rights }: EntityUserRightsProps) => {
  const { t } = useTranslation()

  return (
    <Panel id="users">
      <header>
        <h1>
          <Trans>Utilisateurs</Trans>
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
                request.status === UserRightStatus.Accepted && <div>EDIT</div>,
                request.status !== UserRightStatus.Accepted && (
                  <div>ACCEPT</div>
                ),
                request.status !== UserRightStatus.Accepted && (
                  <div>REJECT</div>
                ),
                request.status === UserRightStatus.Accepted && (
                  <div>REVOKE </div>
                ),
              ])
            ),
          ]}
        />
      )}
    </Panel>
  )
}
