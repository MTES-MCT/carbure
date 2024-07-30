import { memo } from "react"
import { useTranslation } from "react-i18next"
import { Stock } from "../../types"
import {
  formatNumber,
  formatDate,
  formatPeriod,
  formatUnit,
} from "common/utils/formatters"
import Table, { Cell, Order, selectionColumn } from "common/components/table"
import StockTag from "./stock-tag"
import { isRedII } from "lot-add/components/ghg-fields"
import { To } from "react-router-dom"
import useEntity from "carbure/hooks/entity"
import { compact } from "common/utils/collection"

export interface StockTableProps {
  loading: boolean
  stocks: Stock[]
  order: Order | undefined
  selected: number[]
  rowLink: (stock: Stock) => To
  onSelect: (selected: number[]) => void
  onOrder: (order: Order | undefined) => void
  onAction?: (stock: Stock) => void
}

export const StockTable = memo(
  ({
    loading,
    stocks,
    order,
    selected,
    rowLink,
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
        rowLink={rowLink}
        rows={stocks}
        columns={compact([
          selectionColumn(stocks, selected, onSelect, (s: Stock) => s.id),
          columns.status,
          columns.period,
          columns.quantity,
          columns.feedstock,
          columns.supplier,
          columns.productionSite,
          columns.depot,
          columns.ghgReduction,
        ])}
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
    quantity: {
      key: "volume",
      header: t("Biocarburant"),
      cell: (stock: Stock) => <BiofuelCell stock={stock} />,
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
    client: {
      header: t("Client"),
      cell: (stock: Stock) => (
        <Cell text={stock.carbure_client?.name ?? "N/A"} />
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
        return <Cell text={`${reduction.toFixed(0)}%`} />
      },
    },
  }
}

interface StockCellProps {
  stock: Stock
}

export const BiofuelCell = ({ stock }: StockCellProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const unitToField = {
    l: "remaining_volume" as const,
    kg: "remaining_weight" as const,
    MJ: "remaining_lhv_amount" as const,
  }

  const unit = entity.preferred_unit ?? "l"
  const field = unitToField[unit]

  return (
    <Cell
      text={t(stock.biofuel?.code ?? "", { ns: "biofuels" })}
      sub={formatUnit(stock[field], unit)}
    />
  )
}

export default StockTable
