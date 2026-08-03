import { downloadMacFossilFuel } from "accounting/api/mac-fossil-fuel"
import { useAnnualDeclarationTiruert } from "accounting/providers/annual-declaration-tiruert.provider"
import { Button } from "common/components/button2"
import { Download } from "common/components/download"
import { usePortal } from "common/components/portal"
import { Box, Row } from "common/components/scaffold"
import { Title } from "common/components/title"
import useEntity from "common/hooks/entity"
import { MacDialog } from "./mac-dialog"

type MacSectionProps = {
  title: string
  actionLabel: string
  downloadLabel: string
  description?: string
  readOnly?: boolean
  entityId?: number
}

export const MacSection = ({
  title,
  actionLabel,
  downloadLabel,
  description,
  readOnly: isReadOnly,
  entityId,
}: MacSectionProps) => {
  const entity = useEntity()
  const portal = usePortal()

  const { selectedYear } = useAnnualDeclarationTiruert()

  const selectedEntityId = entityId ?? entity.id

  const onAddMac = () => {
    portal((close) => (
      <MacDialog
        onClose={close}
        readOnly={isReadOnly}
        entityId={selectedEntityId}
        year={selectedYear}
      />
    ))
  }

  return (
    <Box>
      <Row>
        <Title is="h1" as="h3">
          {title}
        </Title>
        <Button asideX priority="secondary" onClick={onAddMac}>
          {actionLabel}
        </Button>
      </Row>
      {description && <p>{description}</p>}

      <Download
        label={downloadLabel}
        linkProps={{
          href: downloadMacFossilFuel(selectedEntityId, selectedYear),
        }}
      />
    </Box>
  )
}
