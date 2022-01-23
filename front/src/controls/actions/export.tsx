import { useTranslation } from "react-i18next"
import { Download } from "common-v2/components/icons"
import Button from "common-v2/components/button"
import { LotQuery } from "transactions/types"
import * as api from "../api"

export interface ExportLotsButtonProps {
  query: LotQuery
  selection: number[]
}

export const ExportLotsButton = ({
  query,
  selection,
}: ExportLotsButtonProps) => {
  const { t } = useTranslation()
  return (
    <Button
      icon={Download}
      label={t("Exporter vers Excel")}
      action={() => api.downloadLots(query, selection)}
    />
  )
}
