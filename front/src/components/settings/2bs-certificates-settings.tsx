import React, { useEffect } from "react"
import { EntitySelection } from "../../hooks/helpers/use-entity"
import * as api from "../../services/settings"
import useAPI from "../../hooks/helpers/use-api"
import { Title, Button } from "../system"
import { AlertCircle, Plus } from "../system/icons"
import { Alert } from "../system/alert"
import { SectionHeader, SectionBody, Section } from "../system/section"

type BBSCertificateSettingsProps = {
  entity: EntitySelection
}

const BBSCertificateSettings = ({ entity }: BBSCertificateSettingsProps) => {
  const [requestGet2BS, resolveGet2BS] = useAPI(api.get2BSTradingCertificates); // prettier-ignore

  const entityID = entity?.id
  const certificates = requestGet2BS.data ?? []
  const isEmpty = certificates.length === 0

  useEffect(() => {
    if (entityID) {
      resolveGet2BS(entityID)
    }
  }, [entityID])

  return (
    <Section>
      <SectionHeader>
        <Title>Certificats 2BS</Title>
        <Button level="primary" icon={Plus}>
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
    </Section>
  )
}

export default BBSCertificateSettings
