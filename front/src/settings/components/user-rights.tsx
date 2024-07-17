import { Trans, useTranslation } from "react-i18next"

import { RightStatus } from "account/components/access-rights"
import { Alert } from "common/components/alert"
import Dialog, { Confirm } from "common/components/dialog"
import {
  AlertCircle,
  Check,
  Cross,
  Edit,
  Return,
} from "common/components/icons"
import Table, { actionColumn, Cell } from "common/components/table"
import { useQuery, useMutation } from "common/hooks/async"
import { UserRightRequest, UserRightStatus, UserRole } from "carbure/types"
import * as api from "../api/user-rights"
import { getUserRoleLabel } from "carbure/utils/normalizers"
import { Panel } from "common/components/scaffold"
import useEntity from "carbure/hooks/entity"
import { compact } from "common/utils/collection"
import Button from "common/components/button"
import { usePortal } from "common/components/portal"
import { formatDate } from "common/utils/formatters"
import { useState } from "react"
import { Form } from "common/components/form"
import { RadioGroup } from "common/components/radio"
import { useNotify } from "common/components/notifications"
import { UserRightsTable } from "common/components/user-rights-table"

const RIGHTS_ORDER = {
  [UserRightStatus.Pending]: 0,
  [UserRightStatus.Accepted]: 1,
  [UserRightStatus.Revoked]: 2,
  [UserRightStatus.Rejected]: 3,
}

const EntityUserRights = () => {
  const { t } = useTranslation()
  const entity = useEntity()

  const rights = useQuery(api.getEntityRights, {
    key: "entity-rights",
    params: [entity.id],
  })

  const rows = rights.result?.data.data?.requests ?? []

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
                request.status === UserRightStatus.Accepted && <div></div>,
                request.status !== UserRightStatus.Accepted && (
                  <AcceptUserButton request={request} />
                ),
                request.status !== UserRightStatus.Accepted && (
                  <RejectUserButton request={request} />
                ),
                request.status === UserRightStatus.Accepted && (
                  <RevokeUserButton request={request} />
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
  request: UserRightRequest
}

const AcceptUserButton = ({ request }: UserActionButton) => {
  const { t } = useTranslation()
  const portal = usePortal()
  const entity = useEntity()

  const acceptRight = useMutation(api.acceptUserRightsRequest, {
    invalidates: ["entity-rights"],
  })

  const user = request.user[0]

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
            onConfirm={() => acceptRight.execute(entity.id, request.id)}
            onClose={close}
          />
        ))
      }
    />
  )
}

const RejectUserButton = ({ request }: UserActionButton) => {
  const { t } = useTranslation()
  const portal = usePortal()
  const entity = useEntity()

  const revokeRight = useMutation(api.revokeUserRights, {
    invalidates: ["entity-rights"],
  })

  const user = request.user[0]

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

const RevokeUserButton = ({ request }: UserActionButton) => {
  const { t } = useTranslation()
  const portal = usePortal()
  const entity = useEntity()

  const revokeRight = useMutation(api.revokeUserRights, {
    invalidates: ["entity-rights"],
  })

  const user = request.user[0]

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
  request: UserRightRequest
}

const EntityUserRights2 = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()

  const response = useQuery(api.getEntityRights, {
    key: "entity-rights",
    params: [entity.id],
  })

  const changeUserRole = useMutation(api.changeUserRole, {
    invalidates: ["entity-rights"],

    onSuccess: () => {
      notify(t("Le rôle de l'utilisateur a été modifié !"), {
        variant: "success",
      })
    },
    onError: () => {
      notify(t("Le rôle de l'utilisateur n'a pas pu être modifié !"), {
        variant: "danger",
      })
    },
  })

  const rights = response.result?.data.data?.requests ?? []

  return (
    <UserRightsTable
      rights={rights}
      isLoadingEditUserRight={changeUserRole.loading}
      onChangeUserRole={(role, request) =>
        changeUserRole.execute(entity.id, request.user[0], role!)
      }
      onAcceptUser={() => {}}
      onRevokeUser={() => {}}
      onRejectUser={() => {}}
    />
  )
}

export default EntityUserRights2
