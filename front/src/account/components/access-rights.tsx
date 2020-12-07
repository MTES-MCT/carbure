import { useState } from "react"
import cl from "clsx"

import { Entity } from "common/types"
import { SettingsGetter } from "settings/hooks/use-get-settings"

import statusStyles from "transactions/components/status.module.css"
import colStyles from "transactions/components/list-columns.module.css"
import pendingStyles from "carbure/components/pending.module.css"

import * as common from "common/api"

import { Button, Title } from "common/components"
import { AlertTriangle, Plus } from "common/components/icons"
import { EMPTY_COLUMN, SettingsForm } from "settings/components/common"
import { LabelAutoComplete } from "common/components/autocomplete"
import { Alert } from "common/components/alert"
import Table, { Column, Line, Row } from "common/components/table"
import { Section, SectionBody, SectionHeader } from "common/components/section"
import {
  DialogButtons,
  prompt,
  PromptFormProps,
} from "common/components/dialog"

const EntityPrompt = ({ onConfirm, onCancel }: PromptFormProps<Entity>) => {
  const [entity, setEntity] = useState<Entity | null>(null)

  return (
    <SettingsForm>
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
          onClick={() => entity && onConfirm(entity)}
        >
          Demander l'accès
        </Button>
        <Button onClick={onCancel}>Annuler</Button>
      </DialogButtons>
    </SettingsForm>
  )
}

const Status = ({ status }: { status: string }) => (
  <span
    className={cl(
      statusStyles.status,
      statusStyles.smallStatus,
      status === "ACCEPTED"
        ? statusStyles.statusAccepted
        : statusStyles.statusWaiting
    )}
  >
    {status}
  </span>
)

interface AccessRight {
  status: string
  entity: Entity
  date: Date
}

const COLUMNS: Column<AccessRight>[] = [
  EMPTY_COLUMN,
  {
    header: "Statut",
    className: colStyles.narrowColumn,
    render: (r) => <Status status={r.status} />,
  },
  {
    header: "Organisation",
    render: (r) => <Line text={r.entity.name} />,
  },
  {
    header: "Type",
    render: (r) => <Line text={r.entity.entity_type} />,
  },
  EMPTY_COLUMN,
]

type AccountAccesRightsProps = {
  settings: SettingsGetter
}

export const AccountAccesRights = ({ settings }: AccountAccesRightsProps) => {
  async function askEntity() {
    const entity = await prompt(
      "Ajout organisation",
      "Recherchez la société qui vous emploie pour pouvoir accéder à ses données.",
      EntityPrompt
    )
  }

  const requests = settings.data?.requests ?? []

  const rows: Row<AccessRight>[] = requests.map((r) => ({
    value: { status: r.status, entity: r.entity, date: r.date },
  }))

  return (
    <Section>
      <SectionHeader>
        <Title>Demande d'accès</Title>
        <Button level="primary" icon={Plus} onClick={askEntity}>
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
    </Section>
  )
}
