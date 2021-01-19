import React, { useState } from "react"
import cl from "clsx"

import { DBSCertificateSettingsHook } from "../hooks/use-2bs-certificates"
import { DBSCertificate } from "common/types"

import styles from "./settings.module.css"

import * as common from "common/api"

import { Title, LoaderOverlay } from "common/components"
import { Button } from "common/components/button"
import { AlertCircle, Cross, Plus } from "common/components/icons"
import { Alert } from "common/components/alert"
import { SectionHeader, SectionBody, Section } from "common/components/section"
import { DialogButtons, PromptFormProps } from "common/components/dialog"
import { LabelAutoComplete } from "common/components/autocomplete"
import Table, { Actions, Column, Line } from "common/components/table"
import { EMPTY_COLUMN, ExpirationDate, SettingsForm } from "./common"

export const DBSPrompt = ({
  onConfirm,
  onCancel,
}: PromptFormProps<DBSCertificate>) => {
  const [certificate, setCertificate] = useState<DBSCertificate | null>(null)

  return (
    <SettingsForm>
      <LabelAutoComplete
        label="Certificat 2BS"
        placeholder="Rechercher un certificat 2BS..."
        name="dbs_certificate"
        value={certificate}
        getQuery={common.find2BSCertificates}
        onChange={(e: any) => setCertificate(e.target.value)}
        getValue={(c) => c?.certificate_id ?? ""}
        getLabel={(c) =>
          c?.certificate_id + " - " + c?.certificate_holder ?? ""
        }
      />

      <DialogButtons>
        <Button
          level="primary"
          icon={Plus}
          disabled={!certificate}
          onClick={() => certificate && onConfirm(certificate)}
        >
          Ajouter
        </Button>
        <Button onClick={onCancel}>Annuler</Button>
      </DialogButtons>
    </SettingsForm>
  )
}

const COLUMNS: Column<DBSCertificate>[] = [
  EMPTY_COLUMN,
  { header: "ID", render: (c) => <Line text={c.certificate_id} /> },
  { header: "Détenteur", render: (c) => <Line text={c.certificate_holder} /> },
  { header: "Périmètre", render: (c) => <Line text={c.scope.join(", ")} /> },
]

type DBSCertificateSettingsProps = {
  settings: DBSCertificateSettingsHook
}

const DBSCertificateSettings = ({ settings }: DBSCertificateSettingsProps) => {
  const columns: Column<DBSCertificate>[] = [
    ...COLUMNS,
    {
      header: "Valide jusqu'au",
      render: (c) => (
        <ExpirationDate
          date={c.valid_until}
          updated={c.has_been_updated}
          onUpdate={() => settings.update2BSCertificate(c)}
        />
      ),
    },
    Actions([
      {
        icon: Cross,
        title: "Supprimer le certificat",
        action: settings.delete2BSCertificate,
      },
    ]),
  ]

  const rows = settings.certificates.map((c) => ({
    value: c,
    className: cl(c.has_been_updated && styles.expiredRow),
  }))

  return (
    <Section id="2bs">
      <SectionHeader>
        <Title>Certificats 2BS</Title>
        <Button
          level="primary"
          icon={Plus}
          onClick={settings.add2BSCertificate}
        >
          Ajouter un certificat 2BS
        </Button>
      </SectionHeader>

      {settings.isEmpty && (
        <SectionBody>
          <Alert icon={AlertCircle} level="warning">
            Aucun certificat 2BS trouvé
          </Alert>
        </SectionBody>
      )}

      {!settings.isEmpty && <Table columns={columns} rows={rows} />}

      {settings.isLoading && <LoaderOverlay />}
    </Section>
  )
}

export default DBSCertificateSettings
