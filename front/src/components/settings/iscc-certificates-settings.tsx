import React, { useEffect, useState } from "react"

import { EntitySelection } from "../../hooks/helpers/use-entity"
import { ISCCCertificate } from "../../services/types"

import styles from "./settings.module.css"

import * as api from "../../services/settings"
import * as common from "../../services/common"
import useAPI from "../../hooks/helpers/use-api"

import { Title, Button, Box, LoaderOverlay } from "../system"
import { AlertCircle, Cross, Plus } from "../system/icons"
import { Alert } from "../system/alert"
import { SectionHeader, SectionBody, Section } from "../system/section"
import { confirm, prompt, PromptFormProps } from "../system/dialog"
import { LabelAutoComplete } from "../system/autocomplete"
import { EMPTY_COLUMN } from "."
import Table, { Actions, Column, Line } from "../system/table"

const ISCCPrompt = ({
  onConfirm,
  onCancel,
}: PromptFormProps<ISCCCertificate>) => {
  const [certificate, setCertificate] = useState<ISCCCertificate | null>(null)

  return (
    <Box>
      <LabelAutoComplete
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
  { header: "ID", render: (c) => <Line text={c.certificate_id} /> },
  { header: "Détenteur", render: (c) => <Line text={c.certificate_holder} /> },
  { header: "Valide jusqu'au", render: (c) => <Line text={c.valid_until} /> },
]

type ISCCCertificateSettingsProps = {
  entity: EntitySelection
}

const ISCCCertificateSettings = ({ entity }: ISCCCertificateSettingsProps) => {
  const [requestGetISCC, resolveGetISCC] = useAPI(api.getISCCCertificates); // prettier-ignore
  const [requestAddISCC, resolveAddISCC] = useAPI(api.addISCCCertificate); // prettier-ignore
  const [requestDelISCC, resolveDelISCC] = useAPI(api.deleteISCCCertificate); // prettier-ignore

  const entityID = entity?.id
  const certificates = requestGetISCC.data ?? []

  const isLoading =
    requestGetISCC.loading || requestAddISCC.loading || requestDelISCC.loading

  const isEmpty = certificates.length === 0

  function refresh() {
    if (entityID) {
      resolveGetISCC(entityID)
    }
  }

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

  async function deleteISCCCertificate(iscc: ISCCCertificate) {
    if (
      entityID &&
      (await confirm(
        "Suppresion certificat",
        `Voulez-vous vraiment supprimer le certificat ISCC "${iscc.certificate_id}" ?`
      ))
    ) {
      resolveDelISCC(entityID, iscc.certificate_id).then(refresh)
    }
  }

  useEffect(() => {
    if (entityID) {
      resolveGetISCC(entityID)
    }
  }, [entityID, resolveGetISCC])

  const columns = [
    ...COLUMNS,
    Actions([
      {
        icon: Cross,
        title: "Supprimer le certificat",
        action: deleteISCCCertificate,
      },
    ]),
  ]

  const rows = certificates.map((c) => ({ value: c }))

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

      {!isEmpty && <Table columns={columns} rows={rows} />}

      {isLoading && <LoaderOverlay />}
    </Section>
  )
}

export default ISCCCertificateSettings
