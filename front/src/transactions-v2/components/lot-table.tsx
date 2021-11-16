import { memo } from "react"
import { useTranslation } from "react-i18next"
import {
  formatDate,
  formatNumber,
  formatPeriod,
} from "common-v2/utils/formatters"
import Table, {
  actionColumn,
  Cell,
  Marker,
  markerColumn,
  selectionColumn,
} from "common-v2/components/table"
import { Lot } from "../types"
import { LotTag } from "./status"
import { SendOneButton } from "transactions-v2/actions/send"

export interface LotTableProps {
  loading?: boolean
  lots: Lot[]
  selected: number[]
  onSelect: (selected: number[]) => void
  onAction: (lot: Lot) => void
}

export const LotTable = memo(
  ({ loading, lots, selected, onSelect, onAction }: LotTableProps) => {
    const { t } = useTranslation()
    return (
      <Table
        loading={loading}
        onAction={onAction}
        rows={lots}
        columns={[
          markerColumn(getLotMarker),
          selectionColumn(lots, selected, onSelect, (lot) => lot.id),
          {
            header: t("Statut"),
            cell: (lot) => <LotTag lot={lot} />,
          },
          {
            header: t("Période"),
            cell: (lot) => (
              <Cell
                text={formatPeriod(lot.period)}
                sub={formatDate(lot.delivery_date)}
              />
            ),
          },
          {
            header: t("N° Document"),
            cell: (lot) => (
              <Cell
                text={lot.transport_document_reference}
                sub={lot.transport_document_type}
              />
            ),
          },
          {
            header: t("Biocarburant"),
            cell: (lot) => (
              <Cell
                text={t(lot.biofuel?.name ?? "", { ns: "biofuels" })}
                sub={`${formatNumber(lot.volume)} L`}
              />
            ),
          },
          {
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
                text={lot.carbure_delivery_site?.name ?? lot.unknown_delivery_site}
                sub={t(lot.delivery_site_country?.name ?? "", { ns: "countries" })}
              />
            ),
          },
          {
            small: true,
            header: t("Réd. GES"),
            cell: (lot) => <Cell text={`${lot.ghg_reduction.toFixed(2)}%`} />,
          },
          actionColumn((lot: Lot) => [<SendOneButton icon lot={lot} />]),
        ]}
      />
    )
  }
)

const getLotMarker: Marker<Lot> = (lot) => {
  return undefined
}

export default LotTable