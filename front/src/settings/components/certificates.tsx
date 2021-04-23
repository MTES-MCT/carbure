import { useState } from "react"
import cl from "clsx"

import { Certificate } from "common/types"

import styles from "./settings.module.css"

import { Title, LoaderOverlay } from "common/components"
import { Button } from "common/components/button"
import { AlertCircle, Cross, Plus } from "common/components/icons"
import { Alert } from "common/components/alert"
import { SectionHeader, SectionBody, Section } from "common/components/section"
import {
  Dialog,
  DialogButtons,
  DialogText,
  DialogTitle,
  PromptProps,
} from "common/components/dialog"
import { LabelAutoComplete } from "common/components/autocomplete"
import Table, { Actions, Column, Line, arrow } from "common/components/table"
import { ExpirationDate, SettingsForm } from "./common"
import { padding } from "transactions/components/list-columns"
import { DBSCertificateSettingsHook } from "settings/hooks/use-2bs-certificates"
import { ISCCCertificateSettingsHook } from "settings/hooks/use-iscc-certificates"
import { REDCertCertificateSettingsHook } from "settings/hooks/use-redcert-certificates"
import { SNCertificateSettingsHook } from "settings/hooks/use-national-system-certificates"

type CertificatePromptProps = PromptProps<Certificate> & {
  type: "2BS" | "ISCC" | "REDcert" | "SN"
  title: string
  description: string
  findCertificates: (q: string) => Promise<Certificate[]>
}

export const CertificatePrompt = ({
  type,
  title,
  description,
  findCertificates,
  onResolve,
}: CertificatePromptProps) => {
  const [certificate, setCertificate] = useState<Certificate | null>(null)

  return (
    <Dialog onResolve={onResolve}>
      <DialogTitle text={title} />
      <DialogText text={description} />

      <SettingsForm>
        <LabelAutoComplete
          label={`Certificat ${type}`}
          placeholder={`Rechercher un certificat ${type}...`}
          name="dbs_certificate"
          value={certificate}
          getQuery={findCertificates}
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
            onClick={() => certificate && onResolve(certificate)}
          >
            Ajouter
          </Button>
          <Button onClick={() => onResolve()}>Annuler</Button>
        </DialogButtons>
      </SettingsForm>
    </Dialog>
  )
}

const COLUMNS: Column<Certificate>[] = [
  padding,
  { header: "ID", render: (c) => <Line text={c.certificate_id} /> },
  { header: "Détenteur", render: (c) => <Line text={c.certificate_holder} /> },
  { header: "Périmètre", render: (c) => <Line text={c.scope.join(", ")} /> },
]

type CertificateSettingsProps = {
  type: "2BS" | "ISCC" | "REDcert" | "SN" | "2BS & ISCC & REDcert & SN"
  loading: boolean
  certificates: Certificate[]
  onAdd?: () => void
  onUpdate?: (c: Certificate) => void
  onDelete?: (c: Certificate) => void
}

export const CertificateSettings = ({
  type,
  loading,
  certificates,
  onAdd,
  onUpdate,
  onDelete,
}: CertificateSettingsProps) => {
  const columns: Column<Certificate>[] = [
    ...COLUMNS,
    {
      header: "Valide jusqu'au",
      render: (c) => (
        <ExpirationDate
          date={c.valid_until}
          updated={c.has_been_updated}
          onUpdate={onUpdate ? () => onUpdate(c) : undefined}
        />
      ),
    },
  ]

  if (onDelete) {
    columns.push(
      Actions([
        {
          icon: Cross,
          title: "Supprimer le certificat",
          action: onDelete,
        },
      ])
    )
  } else {
    columns.push(arrow)
  }

  const rows = certificates.map((c) => ({
    value: c,
    className: cl(c.has_been_updated && styles.expiredRow),
    onClick: () => window.open && window.open(c.download_link),
  }))

  return (
    <Section id={type.toLowerCase()}>
      <SectionHeader>
        <Title>Certificats {type}</Title>
        {onAdd && (
          <Button level="primary" icon={Plus} onClick={onAdd}>
            Ajouter un certificat {type}
          </Button>
        )}
      </SectionHeader>

      {certificates.length === 0 && (
        <SectionBody>
          <Alert icon={AlertCircle} level="warning">
            Aucun certificat {type} trouvé
          </Alert>
        </SectionBody>
      )}

      {certificates.length > 0 && <Table columns={columns} rows={rows} />}

      {loading && <LoaderOverlay />}
    </Section>
  )
}

type DBSCertificateSettingsProps = {
  settings: DBSCertificateSettingsHook
}

export const DBSCertificateSettings = ({
  settings,
}: DBSCertificateSettingsProps) => (
  <CertificateSettings
    type="2BS"
    loading={settings.isLoading}
    certificates={settings.certificates}
    onAdd={settings.add2BSCertificate}
    onUpdate={settings.update2BSCertificate}
    onDelete={settings.delete2BSCertificate}
  />
)

type ISCCCertificateSettingsProps = {
  settings: ISCCCertificateSettingsHook
}

export const ISCCCertificateSettings = ({
  settings,
}: ISCCCertificateSettingsProps) => (
  <CertificateSettings
    type="ISCC"
    loading={settings.isLoading}
    certificates={settings.certificates}
    onAdd={settings.addISCCCertificate}
    onUpdate={settings.updateISCCCertificate}
    onDelete={settings.deleteISCCCertificate}
  />
)

type REDCertCertificateSettingsProps = {
  settings: REDCertCertificateSettingsHook
}

export const REDCertCertificateSettings = ({
  settings,
}: REDCertCertificateSettingsProps) => (
  <CertificateSettings
    type="REDcert"
    loading={settings.isLoading}
    certificates={settings.certificates}
    onAdd={settings.addREDCertCertificate}
    onUpdate={settings.updateREDCertCertificate}
    onDelete={settings.deleteREDCertCertificate}
  />
)


type SNCertificateSettingsProps = {
  settings: SNCertificateSettingsHook
}

export const SNCertificateSettings = ({
  settings,
}: SNCertificateSettingsProps) => (
  <CertificateSettings
    type="SN"
    loading={settings.isLoading}
    certificates={settings.certificates}
    onAdd={settings.addSNCertificate}
    onUpdate={settings.updateSNCertificate}
    onDelete={settings.deleteSNCertificate}
  />
)
