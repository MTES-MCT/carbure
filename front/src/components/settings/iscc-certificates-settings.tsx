import React, { useState } from "react"
import { ISCCCertificateSettingsHook } from "../../hooks/settings/use-iscc-certificates"
import { ISCCCertificate } from "../../services/types"

import * as common from "../../services/common"

import { Title, Button, LoaderOverlay } from "../system"
import { AlertCircle, Cross, Plus } from "../system/icons"
import { Alert } from "../system/alert"
import { SectionHeader, SectionBody, Section } from "../system/section"
import { DialogButtons, PromptFormProps } from "../system/dialog"
import { LabelAutoComplete } from "../system/autocomplete"
import { EMPTY_COLUMN, ExpirationDate, SettingsForm } from "."
import Table, { Actions, Column, Line } from "../system/table"

export const ISCCPrompt = ({
  onConfirm,
  onCancel,
}: PromptFormProps<ISCCCertificate>) => {
  const [certificate, setCertificate] = useState<ISCCCertificate | null>(null)

  return (
    <SettingsForm>
      <LabelAutoComplete
        label="Certificat ISCC"
        placeholder="Rechercher un certificat ISCC..."
        name="iscc_certificate"
        value={certificate}
        getQuery={common.findISCCCertificates}
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

const COLUMNS: Column<ISCCCertificate>[] = [
  EMPTY_COLUMN,
  { header: "ID", render: (c) => <Line text={c.certificate_id} /> },
  { header: "Détenteur", render: (c) => <Line text={c.certificate_holder} /> },
  { header: "Périmètre", render: (c) => <Line text={c.scope.join(", ")} /> },
  { header: "Valide jusqu'au", render: (c) => <ExpirationDate date={c.valid_until} /> }, // prettier-ignore
]

type ISCCCertificateSettingsProps = {
  settings: ISCCCertificateSettingsHook
}

const ISCCCertificateSettings = ({
  settings,
}: ISCCCertificateSettingsProps) => {
  const columns = [
    ...COLUMNS,
    Actions([
      {
        icon: Cross,
        title: "Supprimer le certificat",
        action: settings.deleteISCCCertificate,
      },
    ]),
  ]

  const rows = settings.certificates.map((c) => ({ value: c }))

  return (
    <Section>
      <SectionHeader>
        <Title>Certificats ISCC</Title>
        <Button
          level="primary"
          icon={Plus}
          onClick={settings.addISCCCertificate}
        >
          Ajouter un certificat ISCC
        </Button>
      </SectionHeader>

      {settings.isEmpty && (
        <SectionBody>
          <Alert icon={AlertCircle} level="warning">
            Aucun certificat ISCC trouvé
          </Alert>
        </SectionBody>
      )}

      {!settings.isEmpty && <Table columns={columns} rows={rows} />}

      {settings.isLoading && <LoaderOverlay />}
    </Section>
  )
}

export default ISCCCertificateSettings
