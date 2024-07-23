import Button from "common/components/button"
import { Download } from "common/components/icons"
import { useTranslation } from "react-i18next"
import { SafQuery } from "saf/types"

export interface ExportButtonProps {
  asideX?: boolean
  query: SafQuery
  download: (query: SafQuery) => unknown
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
