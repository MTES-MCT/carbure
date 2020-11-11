import React, { useEffect, useState } from "react"

import { EntitySelection } from "../../hooks/helpers/use-entity"
import { ISCCCertificate } from "../../services/types"

import styles from "./settings.module.css"

import * as api from "../../services/settings"
import * as common from "../../services/common"
import useAPI from "../../hooks/helpers/use-api"

import { Title, Button, Box } from "../system"
import { AlertCircle, Plus } from "../system/icons"
import { Alert } from "../system/alert"
import { SectionHeader, SectionBody, Section } from "../system/section"
import { prompt, PromptFormProps } from "../system/dialog"
import AutoComplete from "../system/autocomplete"

const ISCCPrompt = ({
  onConfirm,
  onCancel,
}: PromptFormProps<ISCCCertificate>) => {
  const [certificate, setCertificate] = useState<ISCCCertificate | null>(null)

  return (
    <Box>
      <AutoComplete
        label="Certificat ISCC"
        placeholder="Rechercher un certificat ISCC..."
        name="iscc_certificate"
        value={certificate}
        getQuery={common.findISCCCertificates}
        onChange={(e: any) => setCertificate(e.target.value)}
        getValue={(c) => c?.certificate_id ?? ""}
        getLabel={(c) => c?.certificate_id ?? ""}
      />

      <Box row className={styles.dialogButtons}>
        <Button
          level="primary"
          icon={Plus}
          disabled={!certificate}
          onClick={() => certificate && onConfirm(certificate)}
        >
          Ajouter
        </Button>
        <Button onClick={onCancel}>Annuler</Button>
      </Box>
    </Box>
  )
}

type ISCCCertificateSettingsProps = {
  entity: EntitySelection
}

const ISCCCertificateSettings = ({ entity }: ISCCCertificateSettingsProps) => {
  const [requestGetISCC, resolveGetISCC] = useAPI(api.getISCCTradingCertificates); // prettier-ignore

  const entityID = entity?.id
  const certificates = requestGetISCC.data ?? []
  const isEmpty = certificates.length === 0

  async function createISCCCertificate() {
    const data = await prompt(
      "Ajouter un certificat ISCC",
      "Vous pouvez rechercher parmi les certificats recensés sur Carbure et ajouter celui qui vous correspond.",
      ISCCPrompt
    )

    // @TODO actually add the certificate
  }

  useEffect(() => {
    if (entityID) {
      resolveGetISCC(entityID)
    }
  }, [entityID])

  return (
    <Section>
      <SectionHeader>
        <Title>Certificats ISCC</Title>
        <Button level="primary" icon={Plus} onClick={createISCCCertificate}>
          Ajouter un certificat ISCC
        </Button>
      </SectionHeader>

      {isEmpty && (
        <SectionBody>
          <Alert icon={AlertCircle} level="warning">
            Aucun certificat ISCC trouvé
          </Alert>
        </SectionBody>
      )}
    </Section>
  )
}

export default ISCCCertificateSettings
