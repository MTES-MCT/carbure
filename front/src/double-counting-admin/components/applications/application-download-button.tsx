import useEntity from "carbure/hooks/entity"
import { DownloadLink } from "common/components/button"
import { Col } from "common/components/scaffold"
import { useTranslation } from "react-i18next"
import { DoubleCountingApplicationDetails } from "../../../double-counting/types"

export const ApplicationDownloadButton = ({
  application,
}: {
  application: DoubleCountingApplicationDetails
}) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const excelURL =
    application &&
    `/api/double-counting/admin/applications/details?entity_id=${entity.id}&dca_id=${application.id}&export=true`
  return (
    <Col style={{ gap: "var(--spacing-xs)", marginRight: "auto" }}>
      <DownloadLink
        href={excelURL ?? "#"}
        label={t("Télécharger la demande d'agrément au format excel")}
      />
    </Col>
  )
}
