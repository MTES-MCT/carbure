import { useTranslation } from "react-i18next"
import { Download } from "common-v2/components/icons"
import Button from "common-v2/components/button"
import { LotQuery } from "transactions/types"
import pickApi from "../api"
import useEntity from "carbure/hooks/entity"

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
