import { useState } from "react"
import cl from "clsx"

import { Entity } from "../services/types"
import { SettingsGetter } from "../hooks/helpers/use-get-settings"

import statusStyles from "../components/transaction/transaction-status.module.css"
import colStyles from "../components/transaction/transaction-columns.module.css"
import pendingStyles from "../components/pending.module.css"

import * as common from "../services/common"

import { Button, LabelInput, Title } from "../components/system"
import { AlertTriangle, Edit, Plus } from "../components/system/icons"
import { EMPTY_COLUMN, SettingsForm } from "../components/settings"
import { LabelAutoComplete } from "../components/system/autocomplete"
import { Alert } from "../components/system/alert"
import Table, { Column, Line, Row } from "../components/system/table"
import {
  Section,
  SectionBody,
  SectionHeader,
} from "../components/system/section"
import {
  DialogButtons,
  prompt,
  PromptFormProps,
} from "../components/system/dialog"

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

      <a href="/" className={pendingStyles.link}>
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

const Status = ({ granted }: { granted: boolean }) => (
  <span
    className={cl(
      statusStyles.status,
      statusStyles.smallStatus,
      granted ? statusStyles.statusAccepted : statusStyles.statusWaiting
    )}
  >
    {granted ? "Autorisé" : "En attente"}
  </span>
)

interface AccessRight {
  granted: boolean
  entity: Entity
}

const COLUMNS: Column<AccessRight>[] = [
  EMPTY_COLUMN,
  {
    header: "Statut",
    className: colStyles.narrowColumn,
    render: (r) => <Status granted={r.granted} />,
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

  const rights = settings.data?.rights ?? []

  const rows: Row<AccessRight>[] = rights.map((r) => ({
    value: { granted: true, entity: r.entity },
  }))

  return (
    <Section>
      <SectionHeader>
        <Title>Demande d'accès</Title>
        <Button level="primary" icon={Plus} onClick={askEntity}>
          Ajouter une organisation
        </Button>
      </SectionHeader>

      {rights.length === 0 && (
        <SectionBody>
          <Alert level="warning" icon={AlertTriangle}>
            Aucune autorisation pour ce compte, ajoutez une organisation pour
            continuer.
          </Alert>
        </SectionBody>
      )}

      {rights.length > 0 && <Table columns={COLUMNS} rows={rows} />}
    </Section>
  )
}

type AccountAuthenticationProps = {
  settings: SettingsGetter
}

export const AccountAuthentication = ({
  settings,
}: AccountAuthenticationProps) => {
  return (
    <Section>
      <SectionHeader>
        <Title>Identifiants</Title>
        <Button level="primary" icon={Edit}>
          Modifier mes identifiants
        </Button>
      </SectionHeader>

      <SectionBody>
        <LabelInput
          readOnly
          label="Addresse email"
          defaultValue={settings.data?.email}
        />
      </SectionBody>
    </Section>
  )
}
