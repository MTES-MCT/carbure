import React, { useState } from "react"

import { DBSCertificateSettingsHook } from "../../hooks/settings/use-2bs-certificates"
import { DBSCertificate } from "../../services/types"

import * as common from "../../services/common"

import { Title, Button, LoaderOverlay } from "../system"
import { AlertCircle, Cross, Plus } from "../system/icons"
import { Alert } from "../system/alert"
import { SectionHeader, SectionBody, Section } from "../system/section"
import { DialogButtons, PromptFormProps } from "../system/dialog"
import { LabelAutoComplete } from "../system/autocomplete"
import Table, { Actions, Column, Line } from "../system/table"
import { EMPTY_COLUMN, ExpirationDate, SettingsForm } from "."

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
  { header: "Valide jusqu'au", render: (c) => <ExpirationDate date={c.valid_until} /> }, // prettier-ignore
]

type DBSCertificateSettingsProps = {
  settings: DBSCertificateSettingsHook
}

const DBSCertificateSettings = ({ settings }: DBSCertificateSettingsProps) => {
  const columns = [
    ...COLUMNS,
    Actions([
      {
        icon: Cross,
        title: "Supprimer le certificat",
        action: settings.delete2BSCertificate,
      },
    ]),
  ]

  const rows = settings.certificates.map((c) => ({ value: c }))

  return (
    <Section>
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
