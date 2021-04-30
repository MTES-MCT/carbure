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
import { EntitySelection } from "carbure/hooks/use-entity"
import { SettingsGetter } from "settings/hooks/use-get-settings"

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

const RIGHTS_COLUMNS: Column<UserRightRequest>[] = [
  padding,
  statusColumn,
  {
    header: "Utilisateur",
    render: (r) => r.user[0] ?? "",
  },
  {
    header: "Droits",
    render: (r) => ROLE_LABELS[r.role],
  },
  {
    header: "Date",
    render: (r) => {
      const dateRequested = formatDate(r.date_requested)
      const dateExpired = r.expiration_date ? formatDate(r.expiration_date) : null // prettier-ignore

      return dateExpired
        ? `${dateRequested} (expire le ${dateExpired})`
        : dateRequested
    },
  },
]

const UserRights = ({
  entity,
  settings,
}: {
  entity: EntitySelection
  settings: SettingsGetter
}) => {
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
            title: "Révoquer",
            icon: Cross,
            action: async (r) => {
              const shouldRevoke = await confirm(
                "Révoquer les droits d'un utilisateur",
                `Voulez vous révoquer les droits d'accès de "${r.user[0]}" à votre société ?`
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
            title: "Accepter",
            icon: Check,
            action: async (r) => {
              const shouldAccept = await confirm(
                "Accepter un utilisateur",
                `Voulez vous donner des droits d'accès à votre société à "${r.user[0]}" ?`
              )

              if (shouldAccept) {
                await acceptRight(entityID, r.id)
                getRights(entityID)
              }
            },
          },
          {
            title: "Refuser",
            icon: Cross,
            action: async (r) => {
              const shouldReject = await confirm(
                "Refuser un utilisateur",
                `Voulez vous refuser l'accès à votre société à "${r.user[0]}" ?`
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

  return (
    <Section id="users">
      <SectionHeader>
        <Title>Utilisateurs</Title>
      </SectionHeader>

      <SectionBody>
        {rows.length === 0 && (
          <Alert
            icon={AlertCircle}
            level="warning"
            className={styles.emptyUserRights}
          >
            Aucun utilisateur associé à cette entité
          </Alert>
        )}
      </SectionBody>

      {rows.length > 0 && (
        <Table columns={[...RIGHTS_COLUMNS, actions]} rows={rows} />
      )}
    </Section>
  )
}

export default UserRights
