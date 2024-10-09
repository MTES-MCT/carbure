import Button from "common/components/button"
import { Download } from "common/components/icons"
import { useTranslation } from "react-i18next"
import { SafOperatorQuery } from "saf/types"

export interface ExportButtonProps {
  asideX?: boolean
  query: SafOperatorQuery
  download: (query: SafOperatorQuery) => unknown
}

export const ExportButton = ({
  asideX,
  query,
  download,
}: ExportButtonProps) => {
  const { t } = useTranslation()
  return (
    <Button
      asideX={asideX}
      icon={Download}
      label={t("Exporter vers Excel")}
      action={() => download(query)}
    />
  )
}
