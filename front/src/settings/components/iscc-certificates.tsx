import React, { useState } from "react"
import cl from "clsx"
import { ISCCCertificateSettingsHook } from "../hooks/use-iscc-certificates"
import { ISCCCertificate } from "common/types"

import styles from "./settings.module.css"

import * as common from "common/api"

import { Title, LoaderOverlay } from "common/components"
import { Button } from "common/components/button"
import { AlertCircle, Cross, Plus } from "common/components/icons"
import { Alert } from "common/components/alert"
import { SectionHeader, SectionBody, Section } from "common/components/section"
import { DialogButtons, PromptFormProps } from "common/components/dialog"
import { LabelAutoComplete } from "common/components/autocomplete"
import { EMPTY_COLUMN, ExpirationDate, SettingsForm } from "./common"
import Table, { Actions, Column, Line } from "common/components/table"

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
]

type ISCCCertificateSettingsProps = {
  settings: ISCCCertificateSettingsHook
}

const ISCCCertificateSettings = ({
  settings,
}: ISCCCertificateSettingsProps) => {
  const columns: Column<ISCCCertificate>[] = [
    ...COLUMNS,
    {
      header: "Valide jusqu'au",
      render: (c) => (
        <ExpirationDate
          date={c.valid_until}
          updated={c.has_been_updated}
          onUpdate={() => settings.updateISCCCertificate(c)}
        />
      ),
    },
    Actions([
      {
        icon: Cross,
        title: "Supprimer le certificat",
        action: settings.deleteISCCCertificate,
      },
    ]),
  ]

  const rows = settings.certificates.map((c) => ({
    value: c,
    className: cl(c.has_been_updated && styles.expiredRow),
  }))

  return (
    <Section id="iscc">
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
