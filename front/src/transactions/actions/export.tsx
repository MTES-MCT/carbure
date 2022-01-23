import { useTranslation } from "react-i18next"
import { LotQuery, StockQuery } from "../types"
import { Download } from "common-v2/components/icons"
import Button from "common-v2/components/button"
import * as api from "../api"
import { useMatomo } from "matomo"

export interface ExportLotsButtonProps {
  query: LotQuery
  selection: number[]
}

export const ExportLotsButton = ({
  query,
  selection,
}: ExportLotsButtonProps) => {
  const matomo = useMatomo()
  const { t } = useTranslation()
  return (
    <Button
      asideX
      icon={Download}
      label={t("Exporter vers Excel")}
      action={() => {
        matomo.push([
          "trackEvent",
          "lots",
          "export-lots-excel",
          selection.length,
        ])
        api.downloadLots(query, selection)
      }}
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
  const matomo = useMatomo()
  const { t } = useTranslation()
  return (
    <Button
      asideX
      icon={Download}
      label={t("Exporter vers Excel")}
      action={() => {
        matomo.push([
          "trackEvent",
          "lots",
          "export-stocks-excel",
          selection.length,
        ])
        api.downloadStocks(query, selection)
      }}
    />
  )
}
