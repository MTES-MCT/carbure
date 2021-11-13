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
  Column,
  Marker,
  markerColumn,
  selectionColumn,
} from "common-v2/components/table"
import { Lot } from "../types"
import Status from "./status"
import { SendIconButton } from "transactions-v2/actions/send"

export interface LotTableProps {
  loading?: boolean
  lots: Lot[]
  selected: number[]
  onSelect: (selected: number[]) => void
}

export const LotTable = memo(
  ({ loading, lots, selected, onSelect }: LotTableProps) => {
    const { t } = useTranslation()

    const columns: Record<string, Column<Lot>> = {
      status: {
        small: true,
        header: t("Statut"),
        cell: (lot) => <Status lot={lot} />,
      },

      period: {
        small: true,
        header: t("Période"),
        cell: (lot) => (
          <Cell
            text={formatPeriod(lot.period)}
            sub={formatDate(lot.delivery_date)}
          />
        ),
      },

      transportDocument: {
        header: t("N° Document"),
        cell: (lot) => (
          <Cell
            text={lot.transport_document_reference}
            sub={lot.transport_document_type}
          />
        ),
      },

      biofuel: {
        header: t("Biocarburant"),
        cell: (lot) => (
          <Cell
            text={t(lot.biofuel?.name ?? "", { ns: "biofuels" })}
            sub={`${formatNumber(lot.volume)} L`}
          />
        ),
      },

      feedstock: {
        header: t("Matière première"),
        cell: (lot) => (
          <Cell
            text={t(lot.feedstock?.name ?? "", { ns: "feedstocks" })}
            sub={t(lot.country_of_origin?.name ?? "", { ns: "countries" })}
          />
        ),
      },

      supplier: {
        header: t("Fournisseur"),
        cell: (lot) => (
          <Cell text={lot.carbure_supplier?.name ?? lot.unknown_supplier} />
        ),
      },

      client: {
        header: t("Client"),
        cell: (lot) => (
          <Cell text={lot.carbure_client?.name ?? lot.unknown_client} />
        ),
      },

      productionSite: {
        header: t("Site de production"),
        cell: (lot) => (
          <Cell
            // prettier-ignore
            text={lot.carbure_production_site?.name ?? lot.unknown_production_site}
            sub={t(lot.production_country?.name ?? "", { ns: "countries" })}
          />
        ),
      },

      deliverySite: {
        header: t("Site de livraison"),
        cell: (lot) => (
          <Cell
            text={lot.carbure_delivery_site?.name ?? lot.unknown_delivery_site}
            sub={t(lot.delivery_site_country?.name ?? "", { ns: "countries" })}
          />
        ),
      },

      ghgReduction: {
        small: true,
        header: t("Réd. GES"),
        cell: (lot) => <Cell text={`${lot.ghg_reduction.toFixed(2)}%`} />,
      },
    }

    return (
      <Table
        loading={loading}
        rows={lots}
        columns={[
          markerColumn(getLotMarker),
          selectionColumn(lots, selected, onSelect, (lot) => lot.id),
          columns.status,
          columns.period,
          columns.transportDocument,
          columns.biofuel,
          columns.feedstock,
          columns.client,
          columns.supplier,
          columns.productionSite,
          columns.deliverySite,
          columns.ghgReduction,
          actionColumn((lot: Lot) => [<SendIconButton lot={lot} />]),
        ]}
      />
    )
  }
)

const getLotMarker: Marker<Lot> = (lot) => {
  return undefined
}
