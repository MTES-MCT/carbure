import { useTranslation } from "react-i18next"
import { LotQuery, StockQuery } from "../types"
import { Download } from "common/components/icons"
import Button from "common-v2/components/button"
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
      asideX
      icon={Download}
      label={t("Exporter vers Excel")}
      action={() => api.downloadLots(query, selection)}
    />
  )
}

export interface ExportStockButtonProps {
  query: StockQuery
  selection: number[]
}

export const ExportStocksButton = ({
  query,
  selection,
}: ExportStockButtonProps) => {
  const { t } = useTranslation()
  return (
    <Button
      asideX
      icon={Download}
      label={t("Exporter vers Excel")}
      action={() => api.downloadStocks(query, selection)}
    />
  )
}
