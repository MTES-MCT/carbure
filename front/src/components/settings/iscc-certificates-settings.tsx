import React, { useEffect } from "react"

import { EntitySelection } from "../../hooks/helpers/use-entity"

import * as api from "../../services/settings"
import useAPI from "../../hooks/helpers/use-api"

import { Title, Button } from "../system"
import { AlertCircle, Plus } from "../system/icons"
import { Alert } from "../system/alert"
import { SectionHeader, SectionBody, Section } from "../system/section"

type ISCCCertificateSettingsProps = {
  entity: EntitySelection
}

const ISCCCertificateSettings = ({ entity }: ISCCCertificateSettingsProps) => {
  const [requestGetISCC, resolveGetISCC] = useAPI(api.getISCCTradingCertificates); // prettier-ignore

  const entityID = entity?.id
  const certificates = requestGetISCC.data ?? []
  const isEmpty = certificates.length === 0

  useEffect(() => {
    if (entityID) {
      resolveGetISCC(entityID)
    }
  }, [entityID])

  return (
    <Section>
      <SectionHeader>
        <Title>Certificats ISCC</Title>
        <Button level="primary" icon={Plus}>
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
