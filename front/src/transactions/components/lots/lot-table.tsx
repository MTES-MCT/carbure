import { memo } from "react"
import { useTranslation } from "react-i18next"
import { Lot, LotError } from "transactions/types"
import {
  formatDate,
  formatNumber,
  formatPeriod,
  formatUnit,
} from "common/utils/formatters"
import { isExpiring } from "transactions/utils/deadline"
import Table, {
  Cell,
  Order,
  markerColumn,
  selectionColumn,
  actionColumn,
} from "common/components/table"
import { Alarm } from "common/components/icons"
import LotTag from "./lot-tag"
import { isRedII } from "lot-add/components/ghg-fields"
import { DuplicateOneButton } from "transactions/actions/duplicate"
import Score from "transaction-details/components/score"
import { To } from "react-router-dom"
import useEntity from "carbure/hooks/entity"
import { compact } from "common/utils/collection"

export interface LotTableProps {
  loading: boolean
  lots: Lot[]
  errors: Record<number, LotError[]>
  order: Order | undefined
  selected: number[]
  rowLink: (lot: Lot) => To
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
    rowLink,
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
        rowLink={rowLink}
        rows={lots}
        columns={compact([
          markerColumn<Lot>((lot) => getLotMarker(lot, errors)),
          selectionColumn(lots, selected, onSelect, (lot) => lot.id),
          columns.score,
          columns.status,
          columns.period,
          columns.document,
          columns.quantity,
          columns.feedstock,
          columns.supplier,
          columns.client,
          columns.productionSite,
          columns.depot,
          columns.ghgReduction,
          columns.actions,
        ])}
      />
    )
  }
)

export function useLotColumns() {
  const { t } = useTranslation()
  const entity = useEntity()

  return {
    score: {
      small: true,
      header: t("Score"),
      cell: (lot: Lot) => <Score lot={lot} />,
    },

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

    quantity: {
      key: "volume",
      header: t("Biocarburant"),
      cell: (lot: Lot) => <BiofuelCell lot={lot} />,
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
          text={lot.carbure_production_site?.name ?? lot.unknown_production_site} // prettier-ignore
          sub={t(lot.production_country?.code_pays ?? "", { ns: "countries" })} // prettier-ignore
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
      cell: (lot: Lot) => {
        const reduction = isRedII(lot.delivery_date)
          ? lot.ghg_reduction_red_ii
          : lot.ghg_reduction
        return <Cell text={`${reduction.toFixed(0)}%`} />
      },
    },

    actions: actionColumn((lot: Lot) =>
      compact([
        lot.added_by?.id === entity.id && <DuplicateOneButton icon lot={lot} />,
      ])
    ),
  }
}

interface LotCellProps {
  lot: Lot
}

export const BiofuelCell = ({ lot }: LotCellProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const unitToField = {
    l: "volume" as "volume",
    kg: "weight" as "weight",
    MJ: "lhv_amount" as "lhv_amount",
  }

  const unit = entity.preferred_unit ?? "l"
  const field = unitToField[unit]

  return (
    <Cell
      text={t(lot.biofuel?.code ?? "", { ns: "biofuels" })}
      sub={formatUnit(lot[field], unit)}
    />
  )
}

export const PeriodCell = ({ lot }: LotCellProps) => {
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
