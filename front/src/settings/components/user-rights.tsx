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
import { UserRight, UserRightStatus, UserRole } from "carbure/types"
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
            actionColumn<UserRight>((right) =>
              compact([
                right.status === UserRightStatus.Accepted && (
                  <EditUserRightsButton right={right} />
                ),
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

const EditUserRightsButton = ({ right: request }: UserActionButton) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      captive
      variant="icon"
      icon={Edit}
      title={t("Modifier le rôle")}
      action={() =>
        portal((close) => <UserRoleDialog onClose={close} request={request} />)
      }
    />
  )
}

export interface UserRightsProps {
  onClose: () => void
  request: UserRight
}

export const UserRoleDialog = ({ onClose, request }: UserRightsProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const entity = useEntity()
  const [role, setRole] = useState<UserRole | undefined>(request.role)
  const userEmail = request.user

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

  const handleSubmit = async () => {
    await changeUserRole.execute(entity.id, userEmail, role!)
  }

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Modifier le rôle")}</h1>
      </header>
      <main>
        <section>
          {t("Modifier le rôle de l'utilisateur {{userEmail}} ?", {
            userEmail,
          })}
        </section>
        <section>
          <Form id="access-right" onSubmit={handleSubmit}>
            <RadioGroup
              label={t("Rôle")}
              name="role"
              value={role}
              onChange={setRole}
              options={[
                {
                  value: UserRole.ReadOnly,
                  label: t("Lecture seule (consultation des lots uniquement)"),
                },
                {
                  value: UserRole.ReadWrite,
                  label: t("Lecture/écriture (création et gestion des lots)"),
                },
                {
                  value: UserRole.Admin,
                  label: t("Administration (contrôle complet de la société sur CarbuRe)"), // prettier-ignore
                },
              ]}
            />
          </Form>
        </section>
      </main>
      <footer>
        <Button
          variant="primary"
          loading={changeUserRole.loading}
          icon={Edit}
          label={t("Modifier le rôle")}
          disabled={!entity || !role}
          submit="access-right"
        />
        <Button asideX icon={Return} action={onClose} label={t("Retour")} />
      </footer>
    </Dialog>
  )
}

export default EntityUserRights
