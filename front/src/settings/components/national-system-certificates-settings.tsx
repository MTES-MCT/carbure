import React, { useState } from "react"
import { SettingsForm } from "./common"

import { NationalSystemCertificatesSettingsHook } from "../hooks/use-national-system-certificates"

import { Title, LoaderOverlay, LabelInput, Button } from "common/system"
import { PromptFormProps, DialogButtons } from "common/system/dialog"
import { Edit, Save } from "common/system/icons"
import { SectionHeader, SectionBody, Section } from "common/system/section"

export const NationalSystemCertificatesPromptFactory = (
  currentCertificate: string = ""
) =>
  function NationalSystemCertificatesPrompt({
    onConfirm,
    onCancel,
  }: PromptFormProps<string>) {
    const [certificate, setCertificate] = useState<string>(currentCertificate)

    return (
      <SettingsForm>
        <LabelInput
          label="Certificat Système National"
          value={certificate}
          onChange={(e) => setCertificate(e.target.value)}
        />

        <DialogButtons>
          <Button
            level="primary"
            icon={Save}
            disabled={!certificate}
            onClick={() => certificate && onConfirm(certificate)}
          >
            Sauvegarder
          </Button>
          <Button onClick={onCancel}>Annuler</Button>
        </DialogButtons>
      </SettingsForm>
    )
  }

type NationalSystemCertificatesSettingsProps = {
  settings: NationalSystemCertificatesSettingsHook
}

const NationalSystemCertificatesSettings = ({
  settings,
}: NationalSystemCertificatesSettingsProps) => {
  return (
    <Section>
      <SectionHeader>
        <Title>Certificat Système National</Title>
        <Button
          level="primary"
          icon={Edit}
          onClick={settings.editNationalSystemCertificates}
        >
          Modifier certificat
        </Button>
      </SectionHeader>

      <SectionBody>
        <LabelInput
          readOnly
          label="N° de certificat"
          value={settings.certificateNumber}
        />
      </SectionBody>

      {settings.isLoading && <LoaderOverlay />}
    </Section>
  )
}

export default NationalSystemCertificatesSettings
