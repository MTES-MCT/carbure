import { Trans, useTranslation } from "react-i18next"

import { RightStatus } from "account/components/access-rights"
import { Alert } from "common/components/alert"
import { Confirm } from "common/components/dialog"
import { AlertCircle, Check, Cross } from "common/components/icons"
import Table, { actionColumn, Cell } from "common/components/table"
import { useQuery, useMutation } from "common/hooks/async"
import { UserRight, UserRightStatus, UserRole } from "carbure/types"
import * as api from "../api/user-rights"
import { Panel } from "common/components/scaffold"
import useEntity from "carbure/hooks/entity"
import { compact } from "common/utils/collection"
import Button from "common/components/button"
import { usePortal } from "common/components/portal"
import { formatDate } from "common/utils/formatters"
import { useNotify } from "common/components/notifications"
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

const EntityUserRights = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const portal = usePortal()

  const rights = useQuery(api.getEntityRights, {
    key: "entity-rights",
    params: [entity.id],
  })

  const rows = rights.result?.data.data?.rights ?? []

  return (
    <Panel id="users">
      <header>
        <h1>
          <Trans>Utilisateurs</Trans>
        </h1>
      </header>

      {rows.length === 0 && (
        <>
          <section>
            <Alert icon={AlertCircle} variant="warning">
              <Trans>Aucun utilisateur associé à cette entité</Trans>
            </Alert>
          </section>
          <footer />
        </>
      )}

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
              cell: (r) => <RightStatus status={r.status} />,
            },
            {
              key: "user",
              header: t("Utilisateur"),
              orderBy: (r) => r.user ?? "",
              cell: (r) => <Cell text={r.user ?? ""} />,
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
                  onChange={(role) =>
                    portal((close) => (
                      <UserRoleDialog
                        request={r}
                        role={role!}
                        onClose={close}
                      />
                    ))
                  }
                />
              ),
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
            actionColumn<UserRight>((right) =>
              compact([
                right.status !== UserRightStatus.Accepted && (
                  <AcceptUserButton right={right} />
                ),
                right.status !== UserRightStatus.Accepted && (
                  <RejectUserButton right={right} />
                ),
                right.status === UserRightStatus.Accepted && (
                  <RevokeUserButton right={right} />
                ),
              ])
            ),
          ]}
        />
      )}
    </Panel>
  )
}

interface UserActionButton {
  right: UserRight
}

const AcceptUserButton = ({ right }: UserActionButton) => {
  const { t } = useTranslation()
  const portal = usePortal()
  const entity = useEntity()

  const acceptRight = useMutation(api.acceptUserRightsRequest, {
    invalidates: ["entity-rights"],
  })

  const user = right.user

  return (
    <Button
      captive
      variant="icon"
      icon={Check}
      title={t("Accepter")}
      action={() =>
        portal((close) => (
          <Confirm
            title={t("Accepter un utilisateur")}
            description={t("Voulez vous donner des droits d'accès à votre société à {{user}} ?", { user })} // prettier-ignore
            confirm={t("Accepter")}
            icon={Check}
            variant="success"
            onConfirm={() => acceptRight.execute(entity.id, right.id)}
            onClose={close}
          />
        ))
      }
    />
  )
}

const RejectUserButton = ({ right: request }: UserActionButton) => {
  const { t } = useTranslation()
  const portal = usePortal()
  const entity = useEntity()

  const revokeRight = useMutation(api.revokeUserRights, {
    invalidates: ["entity-rights"],
  })

  const user = request.user

  return (
    <Button
      captive
      variant="icon"
      icon={Cross}
      title={t("Refuser")}
      action={() =>
        portal((close) => (
          <Confirm
            title={t("Refuser un utilisateur")}
            description={t("Voulez vous refuser l'accès à votre société à {{user}} ?", { user })} // prettier-ignore
            confirm={t("Refuser")}
            icon={Cross}
            variant="danger"
            onConfirm={() => revokeRight.execute(entity.id, user)}
            onClose={close}
          />
        ))
      }
    />
  )
}

const RevokeUserButton = ({ right: request }: UserActionButton) => {
  const { t } = useTranslation()
  const portal = usePortal()
  const entity = useEntity()

  const revokeRight = useMutation(api.revokeUserRights, {
    invalidates: ["entity-rights"],
  })

  const user = request.user

  return (
    <Button
      captive
      variant="icon"
      icon={Cross}
      title={t("Révoquer")}
      action={() =>
        portal((close) => (
          <Confirm
            title={t("Révoquer les droits d'un utilisateur")}
            description={t("Voulez vous révoquer les droits d'accès de {{user}} à votre société ?", { user })} // prettier-ignore
            confirm={t("Révoquer")}
            icon={Cross}
            variant="danger"
            onConfirm={() => revokeRight.execute(entity.id, user)}
            onClose={close}
          />
        ))
      }
    />
  )
}

export interface UserRightsProps {
  onClose: () => void
  role: UserRole
  request: UserRight
}

export const UserRoleDialog = ({ onClose, role, request }: UserRightsProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const entity = useEntity()

  const changeUserRole = useMutation(api.changeUserRole, {
    invalidates: ["entity-rights"],

    onSuccess: () => {
      notify(t("Le rôle de l'utilisateur a été modifié !"), {
        variant: "success",
      })
      onClose()
    },
    onError: () => {
      notify(t("Le rôle de l'utilisateur n'a pas pu être modifié !"), {
        variant: "danger",
      })
    },
  })

  return (
    <Confirm
      title={t("Modifier le rôle")}
      description={t(`Voulez vous changer le rôle de cet utilisateur en "{{role}}" ?`, { role: ROLE_LABELS[role] })} // prettier-ignore
      confirm={t("Confirmer")}
      variant="primary"
      onClose={onClose}
      onConfirm={async () =>
        changeUserRole.execute(entity.id, request.user, role!)
      }
    />
  )
}

export default EntityUserRights
