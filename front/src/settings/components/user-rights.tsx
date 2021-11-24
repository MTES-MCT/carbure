import { Trans, useTranslation } from "react-i18next"

import { statusColumn } from "account/components/access-rights"
import { Title } from "common/components"
import { Alert } from "common/components/alert"
import { confirm } from "common/components/dialog"
import { AlertCircle, Check, Cross } from "common/components/icons"
import { Section, SectionBody, SectionHeader } from "common/components/section"
import Table, { Actions, Column } from "common/components/table"
import useAPI from "common/hooks/use-api"
import { UserRightRequest, UserRightStatus, UserRole } from "common/types"
import { useEffect } from "react"
import { formatDate } from "settings/components/common"
import { padding } from "transactions/components/list-columns"
import * as api from "../api"
import styles from "entities/components/user-rights.module.css"
import { Entity } from "carbure/types"

const RIGHTS_ORDER = {
  [UserRightStatus.Pending]: 0,
  [UserRightStatus.Accepted]: 1,
  [UserRightStatus.Revoked]: 2,
  [UserRightStatus.Rejected]: 3,
}

const UserRights = ({ entity }: { entity: Entity }) => {
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

  const roleLabels = {
    [UserRole.ReadOnly]: t("Lecture seule"),
    [UserRole.ReadWrite]: t("Lecture/écriture"),
    [UserRole.Admin]: t("Administration"),
    [UserRole.Auditor]: t("Audit"),
  }

  const columns: Column<UserRightRequest>[] = [
    padding,
    statusColumn,
    {
      header: t("Utilisateur"),
      render: (r) => r.user[0] ?? "",
    },
    {
      header: t("Droits"),
      render: (r) => roleLabels[r.role],
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
    <Section id="users">
      <SectionHeader>
        <Title>
          <Trans>Utilisateurs</Trans>
        </Title>
      </SectionHeader>

      <SectionBody>
        {rows.length === 0 && (
          <Alert
            icon={AlertCircle}
            level="warning"
            className={styles.emptyUserRights}
          >
            <Trans>Aucun utilisateur associé à cette entité</Trans>
          </Alert>
        )}
      </SectionBody>

      {rows.length > 0 && <Table columns={columns} rows={rows} />}
    </Section>
  )
}

export default UserRights
