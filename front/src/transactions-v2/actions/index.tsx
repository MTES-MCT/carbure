import { useTranslation } from "react-i18next"
import Button from "common-v2/components/button"
import { Plus } from "common-v2/components/icons"
import { LotQuery } from "transactions-v2/types"
import * as api from "../api"
import { Download } from "common/components/icons"

export interface ExportButtonProps {
  query: LotQuery
  selection: number[]
}

export const ExportButton = ({ query, selection }: ExportButtonProps) => {
  const { t } = useTranslation()
  return (
    <Button
      icon={Download}
      label={t("Exporter")}
      action={() => api.downloadLots(query, selection)}
    />
  )
}

export const CreateButton = () => {
  const { t } = useTranslation()
  return (
    <Button
      variant="primary"
      icon={Plus}
      label={t("Créer un lot")}
      to="draft/add"
    />
  )
}
