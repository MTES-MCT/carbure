import React, { useEffect, useState } from "react"

import { EntitySelection } from "../../hooks/helpers/use-entity"
import { ISCCCertificate } from "../../services/types"

import styles from "./settings.module.css"

import * as api from "../../services/settings"
import * as common from "../../services/common"
import useAPI from "../../hooks/helpers/use-api"

import { Title, Button, Box, LoaderOverlay } from "../system"
import { AlertCircle, Plus } from "../system/icons"
import { Alert } from "../system/alert"
import { SectionHeader, SectionBody, Section } from "../system/section"
import { prompt, PromptFormProps } from "../system/dialog"
import AutoComplete from "../system/autocomplete"
import { EMPTY_COLUMN } from "."
import Table, { Column } from "../system/table"

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

const COLUMNS: Column<ISCCCertificate>[] = [
  EMPTY_COLUMN,
  { header: "ID", render: (c) => <span>{c.certificate_id}</span> },
  { header: "Détenteur", render: (c) => <span>{c.certificate_holder}</span> },
  { header: "Valide jusqu'au", render: (c) => <span>{c.valid_until}</span> },
]

type ISCCCertificateSettingsProps = {
  entity: EntitySelection
}

const ISCCCertificateSettings = ({ entity }: ISCCCertificateSettingsProps) => {
  const [requestGetISCC, resolveGetISCC] = useAPI(api.getISCCTradingCertificates); // prettier-ignore
  const [requestAddISCC, resolveAddISCC] = useAPI(api.addISCCTradingCertificate); // prettier-ignore

  const entityID = entity?.id
  const certificates = requestGetISCC.data ?? []

  const isLoading = requestGetISCC.loading || requestAddISCC.loading
  const isEmpty = certificates.length === 0

  const rows = certificates.map((c) => ({ value: c }))

  async function createISCCCertificate() {
    const data = await prompt(
      "Ajouter un certificat ISCC",
      "Vous pouvez rechercher parmi les certificats recensés sur Carbure et ajouter celui qui vous correspond.",
      ISCCPrompt
    )

    if (entityID && data) {
      resolveAddISCC(entityID, data.certificate_id).then(() =>
        resolveGetISCC(entityID)
      )
    }
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

      {!isEmpty && <Table columns={COLUMNS} rows={rows} />}

      {isLoading && <LoaderOverlay />}
    </Section>
  )
}

export default ISCCCertificateSettings
