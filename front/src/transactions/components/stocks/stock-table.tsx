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
import { isRedII } from "lot-add/components/ghg-fields"

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
    const columns = useStockColumns()
    return (
      <Table
        loading={loading}
        order={order}
        onAction={onAction}
        onOrder={onOrder}
        rows={stocks}
        columns={[
          selectionColumn(stocks, selected, onSelect, (s: Stock) => s.id),
          columns.status,
          columns.period,
          columns.biofuel,
          columns.feedstock,
          columns.supplier,
          columns.productionSite,
          columns.depot,
          columns.ghgReduction,
        ]}
      />
    )
  }
)

export function useStockColumns() {
  const { t } = useTranslation()

  return {
    status: {
      header: t("Statut"),
      cell: (stock: Stock) => <StockTag stock={stock} />,
    },
    period: {
      header: t("Période"),
      cell: (stock: Stock) => (
        <Cell
          text={formatPeriod(stock.period)}
          sub={formatDate(stock.delivery_date)}
        />
      ),
    },
    biofuel: {
      key: "volume",
      header: t("Biocarburant"),
      cell: (stock: Stock) => (
        <Cell
          text={t(stock.biofuel?.name ?? "", { ns: "biofuels" })}
          sub={`${formatNumber(stock.remaining_volume)} L`} // prettier-ignore
        />
      ),
    },
    feedstock: {
      key: "feedstock",
      header: t("Matière première"),
      cell: (stock: Stock) => (
        <Cell
          text={t(stock.feedstock?.name ?? "", { ns: "feedstocks" })}
          sub={t(stock.country_of_origin?.name ?? "", { ns: "countries" })} // prettier-ignore
        />
      ),
    },
    supplier: {
      header: t("Fournisseur"),
      cell: (stock: Stock) => (
        <Cell text={stock.carbure_supplier?.name ?? stock.unknown_supplier} />
      ),
    },
    productionSite: {
      header: t("Site de production"),
      cell: (stock: Stock) => (
        <Cell
          text={stock.carbure_production_site?.name ?? stock.unknown_production_site} // prettier-ignore
          sub={t(stock.production_country?.name ?? "", { ns: "countries" })} // prettier-ignore
        />
      ),
    },
    depot: {
      header: t("Dépôt"),
      cell: (stock: Stock) => (
        <Cell
          text={stock.depot?.name}
          sub={t(stock.depot?.country?.name ?? "", { ns: "countries" })}
        />
      ),
    },
    ghgReduction: {
      small: true,
      key: "ghg_reduction",
      header: t("Réd. GES"),
      cell: (stock: Stock) => {
        const reduction = isRedII(stock.delivery_date)
          ? stock.ghg_reduction_red_ii
          : stock.ghg_reduction
        return <Cell text={`${reduction.toFixed(2)}%`} />
      },
    },
  }
}

export default StockTable
