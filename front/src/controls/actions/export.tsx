import { useTranslation } from "react-i18next"
import { Download } from "common/components/icons"
import Button from "common/components/button"
import { LotQuery } from "transactions/types"
import pickApi from "../api"
import useEntity from "common/hooks/entity"

export interface ExportLotsButtonProps {
  query: LotQuery
  selection: number[]
}

export const ExportLotsButton = ({
  query,
  selection,
}: ExportLotsButtonProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  return (
    <Button
      icon={Download}
      label={t("Exporter vers Excel")}
      action={() => pickApi(entity).downloadLots(query, selection)}
    />
  )
}
