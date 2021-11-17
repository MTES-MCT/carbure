import { memo } from "react"
import { useTranslation } from "react-i18next"
import { Stock } from "../types"
import { formatNumber, formatDate } from "common-v2/utils/formatters"
import StockTag from "./stock-tag"
import Table, { Cell, selectionColumn } from "common-v2/components/table"

export interface StockTableProps {
  loading?: boolean
  stocks: Stock[]
  selected: number[]
  onSelect: (selected: number[]) => void
  onAction: (stock: Stock) => void
}

export const StockTable = memo(
  ({ loading, stocks, selected, onSelect, onAction }: StockTableProps) => {
    const { t } = useTranslation()
    return (
      <Table
        loading={loading}
        onAction={onAction}
        rows={stocks}
        columns={[
          selectionColumn(stocks, selected, onSelect, (stock) => stock.id),
          {
            small: true,
            header: t("Statut"),
            cell: (stock) => <StockTag stock={stock} />,
          },
          {
            header: t("Date de livraison"),
            cell: (stock) => (
              <Cell text={`${formatDate(stock.delivery_date)}`} />
            ),
          },
          {
            header: t("Biocarburant"),
            cell: (stock) => (
              <Cell
                text={t(stock.biofuel?.name ?? "", { ns: "biofuels" })}
                sub={`${formatNumber(stock.remaining_volume)} L`}
              />
            ),
          },
          {
            header: t("Matière première"),
            cell: (stock) => (
              <Cell
                text={t(stock.feedstock?.name ?? "", { ns: "feedstocks" })}
                sub={t(stock.country_of_origin?.name ?? "", { ns: "countries" })} // prettier-ignore
              />
            ),
          },
          {
            header: t("Fournisseur"),
            cell: (stock) => (
              <Cell
                text={stock.carbure_supplier?.name ?? stock.unknown_supplier}
              />
            ),
          },
          {
            header: t("Site de production"),
            cell: (stock) => (
              <Cell
                text={stock.carbure_production_site?.name ?? stock.unknown_production_site} // prettier-ignore
                sub={t(stock.production_country?.name ?? "", { ns: "countries" })} // prettier-ignore
              />
            ),
          },
          {
            header: t("Dépôt"),
            cell: (stock) => (
              <Cell
                text={stock.depot?.name}
                sub={t(stock.depot?.country?.name ?? "", { ns: "countries" })}
              />
            ),
          },
          {
            small: true,
            header: t("Réd. GES"),
            cell: (stock) => (
              <Cell text={`${stock.ghg_reduction.toFixed(2)}%`} />
            ),
          },
        ]}
      />
    )
  }
)

export default StockTable
