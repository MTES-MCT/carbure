import { memo } from "react"
import { useTranslation } from "react-i18next"
import { Stock } from "../../types"
import {
  formatNumber,
  formatDate,
  formatPeriod,
} from "common-v2/utils/formatters"
import Table, { Cell, Order, selectionColumn } from "common-v2/components/table"
import StockTag from "./stock-tag"

export interface StockTableProps {
  loading: boolean
  stocks: Stock[]
  order: Order | undefined
  selected: number[]
  onSelect: (selected: number[]) => void
  onAction: (stock: Stock) => void
  onOrder: (order: Order | undefined) => void
}

export const StockTable = memo(
  ({
    loading,
    stocks,
    order,
    selected,
    onSelect,
    onAction,
    onOrder,
  }: StockTableProps) => {
    const { t } = useTranslation()
    return (
      <Table
        loading={loading}
        order={order}
        onAction={onAction}
        onOrder={onOrder}
        rows={stocks}
        columns={[
          selectionColumn(stocks, selected, onSelect, (stock) => stock.id),
          {
            header: t("Statut"),
            cell: (stock) => <StockTag stock={stock} />,
          },
          {
            header: t("Période"),
            cell: (stock) => (
              <Cell
                text={formatPeriod(stock.period)}
                sub={formatDate(stock.delivery_date)}
              />
            ),
          },
          {
            key: "volume",
            header: t("Biocarburant"),
            cell: (stock) => (
              <Cell
                text={t(stock.biofuel?.name ?? "", { ns: "biofuels" })}
                sub={`${formatNumber(stock.remaining_volume)} L`} // prettier-ignore
              />
            ),
          },
          {
            key: "feedstock",
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
            key: "ghg_reduction",
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
