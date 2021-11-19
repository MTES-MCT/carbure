import { useTranslation } from "react-i18next"
import { LotQuery } from "../types"
import Button from "common-v2/components/button"
import { Plus } from "common-v2/components/icons"
import { Download } from "common/components/icons"
import * as api from "../api"

export interface ExportButtonProps {
  query: LotQuery
  selection: number[]
}

export const ExportButton = ({ query, selection }: ExportButtonProps) => {
  const { t } = useTranslation()
  return (
    <Button
      asideX
      icon={Download}
      label={t("Exporter vers Excel")}
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
      to="drafts/add"
    />
  )
}
