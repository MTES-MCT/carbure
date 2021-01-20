import React, { useState } from "react"
import { SettingsForm } from "./common"

import { NationalSystemCertificatesSettingsHook } from "../hooks/use-national-system-certificates"

import { Title, LoaderOverlay } from "common/components"
import { LabelInput } from "common/components/input"
import { Button } from "common/components/button"
import { PromptFormProps, DialogButtons } from "common/components/dialog"
import { Edit, Save } from "common/components/icons"
import { SectionHeader, SectionBody, Section } from "common/components/section"

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
    <Section id="csn">
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
