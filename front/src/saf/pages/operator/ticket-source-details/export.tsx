import Button from "common/components/button"
import { Download } from "common/components/icons"
import { CBQueryParams } from "common/hooks/query-builder-2"
import { useTranslation } from "react-i18next"

export interface ExportButtonProps<
  GenericType extends CBQueryParams<ParamsType, Status, Type>,
  ParamsType extends string[],
  Status extends string,
  Type extends string,
> {
  asideX?: boolean
  query: GenericType
  download: (query: GenericType) => unknown
}

export const ExportButton = <
  GenericType extends CBQueryParams<ParamsType, Status, Type>,
  ParamsType extends string[],
  Status extends string,
  Type extends string,
>({
  asideX,
  query,
  download,
}: ExportButtonProps<GenericType, ParamsType, Status, Type>) => {
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
