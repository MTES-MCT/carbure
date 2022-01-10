import { memo } from "react"
import { useTranslation } from "react-i18next"
import { Lot, LotError } from "transactions/types"
import { formatNumber } from "common-v2/utils/formatters"
import Table, {
  Cell,
  Order,
  markerColumn,
  selectionColumn,
} from "common-v2/components/table"
import {
  getLotMarker,
  PeriodCell,
} from "transactions/components/lots/lot-table"
import LotTag from "transactions/components/lots/lot-tag"

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
    const { t } = useTranslation()
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
          {
            header: t("Statut"),
            cell: (lot) => <LotTag lot={lot} />,
          },
          {
            key: "period",
            header: t("Période"),
            cell: (lot) => <PeriodCell lot={lot} />,
          },
          {
            header: t("N° Document"),
            cell: (lot) => (
              <Cell
                text={lot.transport_document_reference?.toUpperCase()}
                sub={lot.transport_document_type}
              />
            ),
          },
          {
            key: "volume",
            header: t("Biocarburant"),
            cell: (lot) => (
              <Cell
                text={t(lot.biofuel?.name ?? "", { ns: "biofuels" })}
                sub={`${formatNumber(lot.volume)} L`}
              />
            ),
          },
          {
            key: "feedstock",
            header: t("Matière première"),
            cell: (lot) => (
              <Cell
                text={t(lot.feedstock?.name ?? "", { ns: "feedstocks" })}
                sub={t(lot.country_of_origin?.name ?? "", { ns: "countries" })}
              />
            ),
          },
          {
            header: t("Fournisseur"),
            cell: (lot) => (
              <Cell text={lot.carbure_supplier?.name ?? lot.unknown_supplier} />
            ),
          },
          {
            header: t("Client"),
            cell: (lot) => (
              <Cell text={lot.carbure_client?.name ?? lot.unknown_client} />
            ),
          },
          {
            header: t("Site de production"),
            cell: (lot) => (
              <Cell
                // prettier-ignore
                text={lot.carbure_production_site?.name ?? lot.unknown_production_site}
                sub={t(lot.production_country?.name ?? "", { ns: "countries" })}
              />
            ),
          },
          {
            header: t("Site de livraison"),
            cell: (lot) => (
              <Cell
                text={lot.carbure_delivery_site?.name ?? lot.unknown_delivery_site} // prettier-ignore
                sub={t(lot.delivery_site_country?.name ?? "", { ns: "countries" })} // prettier-ignore
              />
            ),
          },
          {
            small: true,
            key: "ghg_reduction",
            header: t("Réd. GES"),
            cell: (lot) => <Cell text={`${lot.ghg_reduction.toFixed(2)}%`} />,
          },
        ]}
      />
    )
  }
)

export default LotTable
