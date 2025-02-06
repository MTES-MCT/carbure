import { Button } from "common/components/button2"
import { CBQueryParams } from "common/hooks/query-builder-2"
import { useTranslation } from "react-i18next"

export interface ExportButtonProps<
  GenericType extends CBQueryParams<ParamsType, Status, Type>,
  ParamsType extends string[],
  Status extends string,
  Type extends string,
> {
  query: GenericType
  download: (query: GenericType) => unknown
}

export const ExportButton = <
  GenericType extends CBQueryParams<ParamsType, Status, Type>,
  ParamsType extends string[],
  Status extends string,
  Type extends string,
>({
  query,
  download,
}: ExportButtonProps<GenericType, ParamsType, Status, Type>) => {
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
