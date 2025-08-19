import { Button } from "common/components/button2"
import { QueryConfig } from "common/hooks/new-query-builder"
import { useTranslation } from "react-i18next"
export interface ExportButtonProps<Q> {
  query: Q
  download: (query: Q) => unknown
}

export const ExportButton = <Config extends QueryConfig>({
  query,
  download,
}: ExportButtonProps<Config>) => {
  const { t } = useTranslation()
  return (
    <Button
      iconId="fr-icon-download-fill"
      priority="secondary"
      onClick={() => download(query)}
    >
      {t("Exporter")}
    </Button>
  )
}
