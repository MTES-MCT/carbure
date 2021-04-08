import { useState } from "react"
import cl from "clsx"

import { Entity, UserRightStatus } from "common/types"
import { SettingsGetter } from "settings/hooks/use-get-settings"
import { AccountHook } from "../index"

import statusStyles from "transactions/components/status.module.css"
import colStyles from "transactions/components/list-columns.module.css"
import pendingStyles from "carbure/components/pending.module.css"

import * as common from "common/api"

import { LoaderOverlay, Title } from "common/components"
import { Button } from "common/components/button"
import { AlertTriangle, Plus } from "common/components/icons"
import { SettingsForm } from "settings/components/common"
import { LabelAutoComplete } from "common/components/autocomplete"
import { Alert } from "common/components/alert"
import Table, { Column, Line, Row } from "common/components/table"
import { padding } from "transactions/components/list-columns"
import { Section, SectionBody, SectionHeader } from "common/components/section"
import {
  Dialog,
  DialogButtons,
  DialogText,
  DialogTitle,
  PromptProps,
} from "common/components/dialog"

export const EntityPrompt = ({ onResolve }: PromptProps<Entity>) => {
  const [entity, setEntity] = useState<Entity | null>(null)

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
            onClick={() => entity && onResolve(entity)}
          >
            Demander l'accès
          </Button>
          <Button onClick={() => onResolve()}>Annuler</Button>
        </DialogButtons>
      </SettingsForm>
    </Dialog>
  )
}

const STATUS_LABEL = {
  [UserRightStatus.Pending]: "En attente",
  [UserRightStatus.Accepted]: "Accepté",
  [UserRightStatus.Rejected]: "Refusé",
  [UserRightStatus.Revoked]: "Révoqué",
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

interface AccessRight {
  status: UserRightStatus
  entity: Entity
  date: Date
}

export const statusColumn = {
  header: "Statut",
  className: colStyles.narrowColumn,
  render: (r: AccessRight) => <RightStatus status={r.status} />,
}

const COLUMNS: Column<AccessRight>[] = [
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

  const rows: Row<AccessRight>[] = requests.map((r) => ({
    value: { status: r.status, entity: r.entity, date: r.date },
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

      {requests.length > 0 && <Table columns={COLUMNS} rows={rows} />}

      {account.isLoading && <LoaderOverlay />}
    </Section>
  )
}
