import React, { useEffect, useState } from "react"

import { EntitySelection } from "../../hooks/helpers/use-entity"
import { DBSCertificate } from "../../services/types"

import styles from "./settings.module.css"

import * as api from "../../services/settings"
import * as common from "../../services/common"
import useAPI from "../../hooks/helpers/use-api"

import { Title, Button, Box, LoaderOverlay } from "../system"
import { AlertCircle, Cross, Plus } from "../system/icons"
import { Alert } from "../system/alert"
import { SectionHeader, SectionBody, Section } from "../system/section"
import { confirm, prompt, PromptFormProps } from "../system/dialog"
import AutoComplete from "../system/autocomplete"
import Table, { Actions, Column, Line } from "../system/table"
import { EMPTY_COLUMN } from "."

const DBSPrompt = ({
  onConfirm,
  onCancel,
}: PromptFormProps<DBSCertificate>) => {
  const [certificate, setCertificate] = useState<DBSCertificate | null>(null)

  return (
    <Box>
      <AutoComplete
        label="Certificat 2BS"
        placeholder="Rechercher un certificat 2BS..."
        name="dbs_certificate"
        value={certificate}
        getQuery={common.find2BSCertificates}
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

const COLUMNS: Column<DBSCertificate>[] = [
  EMPTY_COLUMN,
  { header: "ID", render: (c) => <Line text={c.certificate_id} /> },
  { header: "Détenteur", render: (c) => <Line text={c.certificate_holder} /> },
  { header: "Valide jusqu'au", render: (c) => <Line text={c.valid_until} /> },
]

type DBSCertificateSettingsProps = {
  entity: EntitySelection
}

const DBSCertificateSettings = ({ entity }: DBSCertificateSettingsProps) => {
  const [requestGet2BS, resolveGet2BS] = useAPI(api.get2BSTradingCertificates) // prettier-ignore
  const [requestAdd2BS, resolveAdd2BS] = useAPI(api.add2BSTradingCertificate) // prettier-ignore
  const [requestDel2BS, resolveDel2BS] = useAPI(api.delete2BSTradingCertificate) // prettier-ignore

  const entityID = entity?.id
  const certificates = requestGet2BS.data ?? []

  const isLoading =
    requestGet2BS.loading || requestAdd2BS.loading || requestDel2BS.loading

  const isEmpty = certificates.length === 0

  function refresh() {
    if (entityID) {
      resolveGet2BS(entityID)
    }
  }

  async function create2BSCertificate() {
    const data = await prompt(
      "Ajouter un certificat 2BS",
      "Vous pouvez rechercher parmi les certificats recensés sur Carbure et ajouter celui qui vous correspond.",
      DBSPrompt
    )

    if (entityID && data) {
      resolveAdd2BS(entityID, data.certificate_id).then(refresh)
    }
  }

  async function delete2BSCertificate(dbs: DBSCertificate) {
    if (
      entityID &&
      (await confirm(
        "Suppresion certificat",
        `Voulez-vous vraiment supprimer le certificat 2BS "${dbs.certificate_id}" ?`
      ))
    ) {
      resolveDel2BS(entityID, dbs.certificate_id).then(refresh)
    }
  }

  useEffect(() => {
    if (entityID) {
      resolveGet2BS(entityID)
    }
  }, [entityID])

  const columns = [
    ...COLUMNS,
    Actions<DBSCertificate>([
      {
        icon: Cross,
        title: "Supprimer le certificat",
        action: delete2BSCertificate,
      },
    ]),
  ]

  const rows = certificates.map((c) => ({ value: c }))

  return (
    <Section>
      <SectionHeader>
        <Title>Certificats 2BS</Title>
        <Button level="primary" icon={Plus} onClick={create2BSCertificate}>
          Ajouter un certificat 2BS
        </Button>
      </SectionHeader>

      {isEmpty && (
        <SectionBody>
          <Alert icon={AlertCircle} level="warning">
            Aucun certificat 2BS trouvé
          </Alert>
        </SectionBody>
      )}

      {!isEmpty && <Table columns={columns} rows={rows} />}

      {isLoading && <LoaderOverlay />}
    </Section>
  )
}

export default DBSCertificateSettings
