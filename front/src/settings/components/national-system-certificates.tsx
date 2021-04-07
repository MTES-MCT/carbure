import { useState } from "react"
import { SettingsForm } from "./common"

import { NationalSystemCertificatesSettingsHook } from "../hooks/use-national-system-certificates"

import { Title, LoaderOverlay } from "common/components"
import { LabelInput } from "common/components/input"
import { Button } from "common/components/button"
import {
  PromptProps,
  Dialog,
  DialogButtons,
  DialogTitle,
  DialogText,
} from "common/components/dialog"
import { Edit, Save } from "common/components/icons"
import { SectionHeader, SectionBody, Section } from "common/components/section"

type NationalSystemCertificatesPromptProps = PromptProps<string> & {
  currentCertificate?: string
}

export const NationalSystemCertificatePrompt = ({
  currentCertificate = "",
  onResolve,
}: NationalSystemCertificatesPromptProps) => {
  const [certificate, setCertificate] = useState<string>(currentCertificate)

  return (
    <Dialog onResolve={onResolve}>
      <DialogTitle text="Modifier n° de certificat" />
      <DialogText text="Entrez votre numéro de certificat du Système National." />

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
            onClick={() => certificate && onResolve(certificate)}
          >
            Sauvegarder
          </Button>
          <Button onClick={() => onResolve()}>Annuler</Button>
        </DialogButtons>
      </SettingsForm>
    </Dialog>
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
