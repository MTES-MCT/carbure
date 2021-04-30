import { useState } from "react"
import cl from "clsx"

import {
  Entity,
  UserRightRequest,
  UserRightStatus,
  UserRole,
} from "common/types"
import { SettingsGetter } from "settings/hooks/use-get-settings"
import { AccountHook } from "../index"

import statusStyles from "transactions/components/status.module.css"
import colStyles from "transactions/components/list-columns.module.css"
import pendingStyles from "carbure/components/pending.module.css"

import * as common from "common/api"

import { LoaderOverlay, Title } from "common/components"
import { Button } from "common/components/button"
import { AlertTriangle, Cross, Plus } from "common/components/icons"
import { formatDate, SettingsForm } from "settings/components/common"
import { LabelAutoComplete } from "common/components/autocomplete"
import { Alert } from "common/components/alert"
import Table, { Actions, Column, Line, Row } from "common/components/table"
import { padding } from "transactions/components/list-columns"
import { Section, SectionBody, SectionHeader } from "common/components/section"
import {
  confirm,
  Dialog,
  DialogButtons,
  DialogText,
  DialogTitle,
  PromptProps,
} from "common/components/dialog"
import { Label } from "common/components/input"
import RadioGroup from "common/components/radio-group"
import * as api from "../api"
import useAPI from "common/hooks/use-api"

const STATUS_LABEL = {
  [UserRightStatus.Pending]: "En attente",
  [UserRightStatus.Accepted]: "Accepté",
  [UserRightStatus.Rejected]: "Refusé",
  [UserRightStatus.Revoked]: "Révoqué",
}

const ROLE_LABELS_DETAILS = {
  [UserRole.ReadOnly]: "Lecture seule (consultation des lots uniquement)",
  [UserRole.ReadWrite]: "Lecture/écriture (création et gestion des lots)",
  [UserRole.Admin]:
    "Administration (contrôle complet de la société sur CarbuRe)",
  [UserRole.Auditor]: "Audit (accès spécial pour auditeurs)",
}
const ROLE_LABELS = {
  [UserRole.ReadOnly]: "Lecture seule",
  [UserRole.ReadWrite]: "Lecture/écriture",
  [UserRole.Admin]: "Administration",
  [UserRole.Auditor]: "Audit",
}

const ROLE_OPTIONS = Object.entries(ROLE_LABELS_DETAILS).map(
  ([value, label]) => ({
    value,
    label,
  })
)

export type AccessRequest = {
  entity: Entity
  role: UserRole
}

export const EntityPrompt = ({ onResolve }: PromptProps<AccessRequest>) => {
  const [entity, setEntity] = useState<Entity | null>(null)
  const [role, setRole] = useState<UserRole>(UserRole.ReadOnly)

  return (
    <Dialog onResolve={onResolve}>
      <SettingsForm>
        <DialogTitle text="Ajout organisation" />
        <DialogText text="Recherchez la société qui vous emploie pour pouvoir accéder à ses données." />
        <LabelAutoComplete
          label="Organisation"
          placeholder="Rechercher une société..."
          name="entity"
          value={entity}
          getQuery={common.findEntities}
          onChange={(e: any) => setEntity(e.target.value)}
          getValue={(e) => `${e.id}`}
          getLabel={(e) => e.name}
        />
        <Label label="Rôle">
          <RadioGroup
            name="role"
            options={ROLE_OPTIONS}
            value={role}
            onChange={(e) => setRole(e.target.value as UserRole)}
          />
        </Label>
        <a
          href="mailto:carbure@beta.gouv.fr"
          target="_blank"
          rel="noreferrer"
          className={pendingStyles.link}
        >
          Ma société n'est pas enregistrée sur CarbuRe.
        </a>
        <DialogButtons>
          <Button
            level="primary"
            icon={Plus}
            disabled={!entity}
            onClick={() => entity && onResolve({ entity, role })}
          >
            Demander l'accès
          </Button>
          <Button onClick={() => onResolve()}>Annuler</Button>
        </DialogButtons>
      </SettingsForm>
    </Dialog>
  )
}

export const RightStatus = ({ status }: { status: UserRightStatus }) => (
  <span
    className={cl(
      statusStyles.status,
      statusStyles.smallStatus,
      status === UserRightStatus.Accepted && statusStyles.statusAccepted,
      status === UserRightStatus.Pending && statusStyles.statusWaiting,
      status === UserRightStatus.Rejected && statusStyles.statusRejected,
      status === UserRightStatus.Revoked && statusStyles.statusToFix
    )}
  >
    {STATUS_LABEL[status]}
  </span>
)

export const statusColumn = {
  header: "Statut",
  className: colStyles.narrowColumn,
  render: (r: UserRightRequest) => <RightStatus status={r.status} />,
}

const COLUMNS: Column<UserRightRequest>[] = [
  padding,
  statusColumn,
  {
    header: "Organisation",
    render: (r) => <Line text={r.entity.name} />,
  },
  {
    header: "Type",
    render: (r) => <Line text={r.entity.entity_type} />,
  },
  {
    header: "Droits",
    render: (r) => <Line text={ROLE_LABELS[r.role]} />,
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
  padding,
]

type AccountAccesRightsProps = {
  settings: SettingsGetter
  account: AccountHook
}

export const AccountAccesRights = ({
  settings,
  account,
}: AccountAccesRightsProps) => {
  const requests = settings.data?.requests ?? []
  const [, revokeMyself] = useAPI(api.revokeMyself)

  const actions = Actions<UserRightRequest>([
    {
      title: "Annuler",
      icon: Cross,
      action: async (r) => {
        const shouldRevoke = await confirm(
          "Annuler mes accès",
          `Voulez vous annuler votre accès à ${r.entity.name} ?`
        )

        if (shouldRevoke) {
          await revokeMyself(r.entity.id)
          settings.resolve()
        }
      },
    },
  ])

  const rows: Row<UserRightRequest>[] = requests.map((r) => ({
    value: r,
  }))

  return (
    <Section>
      <SectionHeader>
        <Title>Demandes d'accès aux sociétés</Title>
        <Button level="primary" icon={Plus} onClick={account.askEntityAccess}>
          Ajouter une organisation
        </Button>
      </SectionHeader>

      {requests.length === 0 && (
        <SectionBody>
          <Alert level="warning" icon={AlertTriangle}>
            Aucune autorisation pour ce compte, ajoutez une organisation pour
            continuer.
          </Alert>
        </SectionBody>
      )}

      {requests.length > 0 && (
        <Table columns={[...COLUMNS, actions]} rows={rows} />
      )}

      {account.isLoading && <LoaderOverlay />}
    </Section>
  )
}
