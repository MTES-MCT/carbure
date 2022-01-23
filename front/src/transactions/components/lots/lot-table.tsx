import { memo } from "react"
import { useTranslation } from "react-i18next"
import { Lot, LotError } from "transactions/types"
import {
  formatDate,
  formatNumber,
  formatPeriod,
} from "common-v2/utils/formatters"
import { isExpiring } from "common-v2/utils/deadline"
import Table, {
  Cell,
  Order,
  markerColumn,
  selectionColumn,
} from "common-v2/components/table"
import { Alarm } from "common-v2/components/icons"
import LotTag from "./lot-tag"

export interface LotTableProps {
  loading: boolean
  lots: Lot[]
  errors: Record<number, LotError[]>
  order: Order | undefined
  selected: number[]
  onSelect: (selected: number[]) => void
  onAction: (lot: Lot) => void
  onOrder: (order: Order | undefined) => void
}

export const LotTable = memo(
  ({
    loading,
    lots,
    errors,
    order,
    selected,
    onSelect,
    onAction,
    onOrder,
  }: LotTableProps) => {
    const columns = useLotColumns()
    return (
      <Table
        loading={loading}
        order={order}
        onAction={onAction}
        onOrder={onOrder}
        rows={lots}
        columns={[
          markerColumn<Lot>((lot) => getLotMarker(lot, errors)),
          selectionColumn(lots, selected, onSelect, (lot) => lot.id),
          columns.status,
          columns.period,
          columns.document,
          columns.volume,
          columns.feedstock,
          columns.supplier,
          columns.client,
          columns.productionSite,
          columns.depot,
          columns.ghgReduction,
        ]}
      />
    )
  }
)

export function useLotColumns() {
  const { t } = useTranslation()

  return {
    status: {
      header: t("Statut"),
      cell: (lot: Lot) => <LotTag lot={lot} />,
    },

    period: {
      key: "period",
      header: t("Période"),
      cell: (lot: Lot) => <PeriodCell lot={lot} />,
    },

    document: {
      header: t("N° Document"),
      cell: (lot: Lot) => (
        <Cell
          text={lot.transport_document_reference?.toUpperCase()}
          sub={lot.transport_document_type}
        />
      ),
    },

    volume: {
      key: "volume",
      header: t("Biocarburant"),
      cell: (lot: Lot) => (
        <Cell
          text={t(lot.biofuel?.code ?? "", { ns: "biofuels" })}
          sub={`${formatNumber(lot.volume)} L`}
        />
      ),
    },

    feedstock: {
      key: "feedstock",
      header: t("Matière première"),
      cell: (lot: Lot) => (
        <Cell
          text={t(lot.feedstock?.code ?? "", { ns: "feedstocks" })}
          sub={t(lot.country_of_origin?.code_pays ?? "", { ns: "countries" })} // prettier-ignore
        />
      ),
    },

    supplier: {
      header: t("Fournisseur"),
      cell: (lot: Lot) => (
        <Cell text={lot.carbure_supplier?.name ?? lot.unknown_supplier} />
      ),
    },

    client: {
      header: t("Client"),
      cell: (lot: Lot) => (
        <Cell text={lot.carbure_client?.name ?? lot.unknown_client} />
      ),
    },

    productionSite: {
      header: t("Site de production"),
      cell: (lot: Lot) => (
        <Cell
          // prettier-ignore
          text={lot.carbure_production_site?.name ?? lot.unknown_production_site}
          sub={t(lot.production_country?.code_pays ?? "", {
            ns: "countries",
          })}
        />
      ),
    },

    depot: {
      header: t("Site de livraison"),
      cell: (lot: Lot) => (
        <Cell
          text={lot.carbure_delivery_site?.name ?? lot.unknown_delivery_site} // prettier-ignore
          sub={t(lot.delivery_site_country?.code_pays ?? "", { ns: "countries" })} // prettier-ignore
        />
      ),
    },

    ghgReduction: {
      small: true,
      key: "ghg_reduction",
      header: t("Réd. GES"),
      cell: (lot: Lot) => <Cell text={`${lot.ghg_reduction.toFixed(2)}%`} />,
    },
  }
}
interface PeriodCellProps {
  lot: Lot
}

export const PeriodCell = ({ lot }: PeriodCellProps) => {
  const expiring = isExpiring(lot)
  return (
    <Cell
      icon={expiring ? Alarm : undefined}
      variant={expiring ? "warning" : undefined}
      text={formatPeriod(lot.period)}
      sub={formatDate(lot.delivery_date)}
    />
  )
}

export const getLotMarker = (lot: Lot, errors: Record<number, LotError[]>) => {
  if (!errors[lot.id]) {
    return undefined
  } else if (errors[lot.id].some((err) => err.is_blocking)) {
    return "danger"
  } else if (errors[lot.id].some((err) => !err.is_blocking)) {
    return "warning"
  }
}

export default LotTable
