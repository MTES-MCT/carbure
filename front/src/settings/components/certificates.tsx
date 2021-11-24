import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import cl from "clsx"

import { Certificate, UserRole } from "common/types"

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
import { useRights } from "carbure/hooks/entity"

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
  const { t } = useTranslation()
  const [certificate, setCertificate] = useState<Certificate | null>(null)

  return (
    <Dialog onResolve={onResolve}>
      <DialogTitle text={title} />
      <DialogText text={description} />

      <SettingsForm>
        <LabelAutoComplete
          label={t("Certificat {{type}}", { type })}
          placeholder={t("Rechercher un certificat {{type}}...", { type })}
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
            <Trans>Ajouter</Trans>
          </Button>
          <Button onClick={() => onResolve()}>
            <Trans>Annuler</Trans>
          </Button>
        </DialogButtons>
      </SettingsForm>
    </Dialog>
  )
}

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
  const { t } = useTranslation()
  const rights = useRights()

  const canModify = rights.is(UserRole.Admin, UserRole.ReadWrite)

  const columns: Column<Certificate>[] = [
    padding,
    { header: t("ID"), render: (c) => <Line text={c.certificate_id} /> },
    {
      header: t("Détenteur"),
      render: (c) => <Line text={c.certificate_holder} />,
    },
    {
      header: t("Périmètre"),
      render: (c) => <Line text={c.scope.join(", ")} />,
    },
    {
      header: t("Valide jusqu'au"),
      render: (c) => (
        <ExpirationDate
          date={c.valid_until}
          updated={c.has_been_updated}
          onUpdate={onUpdate ? () => onUpdate(c) : undefined}
        />
      ),
    },
  ]

  if (canModify && onDelete) {
    columns.push(
      Actions([
        {
          icon: Cross,
          title: t("Supprimer le certificat"),
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
        <Title>
          <Trans>Certificats {{ type }}</Trans>
        </Title>
        {onAdd && canModify && (
          <Button level="primary" icon={Plus} onClick={onAdd}>
            <Trans>Ajouter un certificat {{ type }}</Trans>
          </Button>
        )}
      </SectionHeader>

      {certificates.length === 0 && (
        <SectionBody>
          <Alert icon={AlertCircle} level="warning">
            <Trans>Aucun certificat {{ type }} trouvé</Trans>
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
