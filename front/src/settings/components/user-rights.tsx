import { Trans, useTranslation } from "react-i18next"

import { RightStatus } from "account/components/access-rights"
import { Alert } from "common/components/alert"
import { confirm } from "common/components/dialog"
import { AlertCircle, Check, Cross } from "common-v2/components/icons"
import Table, { Actions, Column, padding } from "common/components/table"
import useAPI from "common/hooks/use-api"
import { UserRightRequest, UserRightStatus } from "carbure/types"
import { useEffect } from "react"
import { formatDate } from "settings/components/common"
import * as api from "../api"
import styles from "entities/components/user-rights.module.css"
import colStyles from "common/components/table.module.css"
import { Entity } from "carbure/types"
import { getUserRoleLabel } from "common-v2/utils/normalizers"
import { Panel } from "common-v2/components/scaffold"

const RIGHTS_ORDER = {
  [UserRightStatus.Pending]: 0,
  [UserRightStatus.Accepted]: 1,
  [UserRightStatus.Revoked]: 2,
  [UserRightStatus.Rejected]: 3,
}

const EntityUserRights = ({ entity }: { entity: Entity }) => {
  const { t } = useTranslation()

  const [rights, getRights] = useAPI(api.getEntityRights)
  const [, acceptRight] = useAPI(api.acceptUserRightsRequest)
  const [, revokeRight] = useAPI(api.revokeUserRights)

  const entityID = entity?.id ?? -1

  useEffect(() => {
    getRights(entityID)
  }, [getRights, entityID])

  const rows = (rights.data?.requests ?? [])
    .map((r) => ({ value: r }))
    .sort((a, b) => RIGHTS_ORDER[a.value.status] - RIGHTS_ORDER[b.value.status])

  // available actions are different depending on the status of the user
  const actions = Actions<UserRightRequest>((right) => {
    switch (right.status) {
      case UserRightStatus.Accepted:
        return [
          {
            title: t("Révoquer"),
            icon: Cross,
            action: async (r) => {
              const shouldRevoke = await confirm(
                t("Révoquer les droits d'un utilisateur"),
                t("Voulez vous révoquer les droits d'accès de {{user}} à votre société ?", { user: r.user[0] }) // prettier-ignore
              )

              if (shouldRevoke) {
                await revokeRight(entityID, r.user[0])
                getRights(entityID)
              }
            },
          },
        ]

      case UserRightStatus.Pending:
      case UserRightStatus.Rejected:
      case UserRightStatus.Revoked:
        return [
          {
            title: t("Accepter"),
            icon: Check,
            action: async (r) => {
              const shouldAccept = await confirm(
                t("Accepter un utilisateur"),
                t("Voulez vous donner des droits d'accès à votre société à {{user}} ? ", { user: r.user[0] }) // prettier-ignore
              )

              if (shouldAccept) {
                await acceptRight(entityID, r.id)
                getRights(entityID)
              }
            },
          },
          {
            title: t("Refuser"),
            icon: Cross,
            action: async (r) => {
              const shouldReject = await confirm(
                t("Refuser un utilisateur"),
                t("Voulez vous refuser l'accès à votre société à {{user}} ?", { user: r.user[0] }) // prettier-ignore
              )

              if (shouldReject) {
                await revokeRight(entityID, r.user[0])
                getRights(entityID)
              }
            },
          },
        ]

      default:
        return []
    }
  })

  const columns: Column<UserRightRequest>[] = [
    padding,
    {
      header: "Statut",
      className: colStyles.narrowColumn,
      render: (r: UserRightRequest) => <RightStatus status={r.status} />,
    },
    {
      header: t("Utilisateur"),
      render: (r) => r.user[0] ?? "",
    },
    {
      header: t("Droits"),
      render: (r) => getUserRoleLabel(r.role),
    },
    {
      header: t("Date"),
      render: (r) => {
        const dateRequested = formatDate(r.date_requested)
        const dateExpired = r.expiration_date ? formatDate(r.expiration_date) : null // prettier-ignore

        return dateExpired
          ? t("{{dateRequested}} (expire le {{dateExpired}})", { dateRequested, dateExpired }) // prettier-ignore
          : dateRequested
      },
    },
    actions,
  ]

  return (
    <Panel id="users">
      <header>
        <h1>
          <Trans>Utilisateurs</Trans>
        </h1>
      </header>

      {rows.length === 0 && (
        <section style={{ marginBottom: "var(--spacing-l)" }}>
          <Alert
            icon={AlertCircle}
            level="warning"
            className={styles.emptyUserRights}
          >
            <Trans>Aucun utilisateur associé à cette entité</Trans>
          </Alert>
        </section>
      )}

      {rows.length > 0 && <Table columns={columns} rows={rows} />}
    </Panel>
  )
}

export default EntityUserRights
