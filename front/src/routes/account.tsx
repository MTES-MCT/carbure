import { useState } from "react"
import cl from "clsx"

import { SettingsGetter } from "../hooks/helpers/use-get-settings"

import statusStyles from "../components/transaction/transaction-status.module.css"

import * as common from "../services/common"
import { Button, LabelInput, Main, Title } from "../components/system"
import { AlertTriangle, Edit, Plus } from "../components/system/icons"
import {
  SettingsHeader,
  SettingsBody,
  EMPTY_COLUMN,
  SettingsForm,
} from "../components/settings"
import {
  Section,
  SectionBody,
  SectionHeader,
} from "../components/system/section"
import Table, { Column, Line, Row } from "../components/system/table"
import { Entity, EntityType } from "../services/types"
import {
  DialogButtons,
  prompt,
  PromptFormProps,
} from "../components/system/dialog"
import { LabelAutoComplete } from "../components/system/autocomplete"
import { Alert } from "../components/system/alert"

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

const EntityPrompt = ({ onConfirm, onCancel }: PromptFormProps<Entity>) => {
  const [entity, setEntity] = useState<Entity | null>(null)

  return (
    <SettingsForm>
      <LabelAutoComplete
        label="Organisation"
        placeholder="Rechercher une société.."
        name="entity"
        value={entity}
        getQuery={common.findEntities}
        onChange={(e: any) => setEntity(e.target.value)}
        getValue={(e) => `${e.id}`}
        getLabel={(e) => e.name}
      />

      <span
        style={{
          color: "var(--blue-medium)",
          textDecoration: "underline",
          margin: "16px 0",
        }}
      >
        Ma société n'est pas enregistrée sur CarbuRe.
      </span>

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
interface AccessRight {
  granted: boolean
  entity: Entity
}

const COLUMNS: Column<AccessRight>[] = [
  EMPTY_COLUMN,
  {
    header: "Statut",
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

const ROWS: Row<AccessRight>[] = [
  {
    value: {
      granted: false,
      entity: {
        id: 0,
        has_mac: false,
        has_trading: false,
        entity_type: EntityType.Producer,
        name: "Producteur Test MTES",
        national_system_certificate: "",
      },
    },
  },
  {
    value: {
      granted: false,
      entity: {
        id: 0,
        has_mac: false,
        has_trading: false,
        entity_type: EntityType.Operator,
        name: "Opérateur Test MTES",
        national_system_certificate: "",
      },
    },
  },
]

type AccountProps = {
  settings: SettingsGetter
}

const Account = ({ settings }: AccountProps) => {
  async function askEntity() {
    const entity = await prompt(
      "Ajout organisation",
      "Recherchez la société qui vous emploie pour pouvoir accéder à ses données.",
      EntityPrompt
    )
  }

  return (
    <Main>
      <SettingsHeader>
        <Title>Mon compte</Title>
      </SettingsHeader>

      <SettingsBody>
        <Section>
          <SectionHeader>
            <Title>Demande d'accès</Title>
            <Button level="primary" icon={Plus} onClick={askEntity}>
              Ajouter une organisation
            </Button>
          </SectionHeader>

          <SectionBody>
            <Alert level="warning" icon={AlertTriangle}>
              Aucune autorisation pour ce compte, ajoutez une organisation pour
              continuer.
            </Alert>
          </SectionBody>

          {/* <Table columns={COLUMNS} rows={ROWS} /> */}
        </Section>

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
      </SettingsBody>
    </Main>
  )
}
export default Account
