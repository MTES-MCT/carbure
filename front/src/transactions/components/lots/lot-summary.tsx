import { Trans, useTranslation } from "react-i18next"
import { useQuery } from "common/hooks/async"
import * as api from "../../api"
import { LotQuery, SummaryItem } from "../../types"
import {
  formatNumber,
  formatPercentage,
  formatUnit,
} from "common/utils/formatters"
import { getDeliveryLabel } from "carbure/utils/normalizers"
import { toSearchParams } from "common/services/api"
import { usePortal } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import Alert from "common/components/alert"
import Button, { ExternalLink } from "common/components/button"
import Dialog from "common/components/dialog"
import Table, { Cell } from "common/components/table"
import { Filter, Return } from "common/components/icons"
import { FilterManager, ResetButton } from "../filters"
import NoResult from "../../../common/components/no-result"
import { compact } from "common/utils/collection"
import useEntity from "carbure/hooks/entity"

export interface LotSummaryBarProps extends Partial<FilterManager> {
  query: LotQuery
  selection: number[]
  getSummary?: typeof api.getLotsSummary
  renderSummary?: typeof LotSummary
}

export const LotSummaryBar = ({
  query,
  selection,
  filters,
  onFilter,
  getSummary = api.getLotsSummary,
  renderSummary = LotSummary,
}: LotSummaryBarProps) => {
  const { t } = useTranslation()
  const portal = usePortal()
  const entity = useEntity()

  const summary = useQuery(getSummary, {
    key: "lots-summary",
    params: [query, selection, true],
  })

  const unitToField = {
    l: "total_volume" as "total_volume",
    kg: "total_weight" as "total_weight",
    MJ: "total_lhv_amount" as "total_lhv_amount",
  }

  const unit = entity.preferred_unit ?? "l"
  const field = unitToField[unit]

  const summaryData = summary.result?.data.data ?? {
    count: 0,
    total_volume: 0,
    total_weight: 0,
    total_lhv_amount: 0,
  }

  return (
    <Alert loading={summary.loading} icon={Filter} variant="info">
      <p>
        <Trans
          defaults="<b>{{amount}} lots</b> pour un total de <b>{{volume}}</b>"
          count={summaryData.count}
          values={{
            amount: formatNumber(summaryData.count),
            volume: formatUnit(summaryData[field], unit),
          }}
        ></Trans>
      </p>

      <Button
        variant="link"
        label={t("Voir le récapitulatif")}
        action={() =>
          portal((close) => (
            <LotSummaryDialog
              query={query}
              selection={selection}
              onClose={close}
              renderSummary={renderSummary}
              getSummary={getSummary}
            />
          ))
        }
      />

      {filters && onFilter && (
        <ResetButton filters={filters} onFilter={onFilter} />
      )}
    </Alert>
  )
}

export interface LotSummaryDialogProps {
  query: LotQuery
  selection: number[]
  onClose: () => void
  renderSummary?: typeof LotSummary
  getSummary?: typeof api.getLotsSummary
}

export const LotSummaryDialog = ({
  query,
  selection,
  onClose,
  renderSummary: Summary = LotSummary,
  getSummary,
}: LotSummaryDialogProps) => {
  const { t } = useTranslation()

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Récapitulatif des lots")}</h1>
      </header>

      <main>
        <section>
          {t(
            "Ce tableau résume les informations principales des lots correspondant à votre recherche ou sélection."
          )}
        </section>

        <Summary query={query} selection={selection} getSummary={getSummary} />
      </main>

      <footer>
        <Button asideX icon={Return} label={t("Retour")} action={onClose} />
      </footer>
    </Dialog>
  )
}

export interface LotSummaryProps {
  pending?: boolean
  query: LotQuery
  selection?: number[]
  getSummary?: typeof api.getLotsSummary
}

const EMPTY: number[] = []

export const LotSummary = ({
  pending,
  query,
  selection = EMPTY,
  getSummary = api.getLotsSummary,
}: LotSummaryProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const summary = useQuery(getSummary, {
    key: "lots-summary-details",
    params: [query, selection],
  })

  const columns = useSummaryColumns(query)

  const summaryData = summary.result?.data.data

  const unitToField = {
    l: "volume_sum" as "volume_sum",
    kg: "weight_sum" as "weight_sum",
    MJ: "lhv_amount_sum" as "lhv_amount_sum",
  }

  const unit = entity.preferred_unit ?? "l"
  const field = unitToField[unit]

  const input = summaryData?.in ?? []
  const inputLots = input.reduce((count, item) => count + item.total, 0)
  const inputQuantity = input.reduce((quantity, item) => quantity + item[field], 0) // prettier-ignore

  const output = summaryData?.out ?? []
  const outputLots = output.reduce((count, item) => count + item.total, 0)
  const outputQuantity = output.reduce((quantity, item) => quantity + item[field], 0) // prettier-ignore

  return (
    <>
      {input.length === 0 && output.length === 0 && (
        <section>
          <NoResult />
        </section>
      )}

      {input.length > 0 && (
        <>
          <h2>
            {t("Lots reçus")}
            {" ▸ "}
            {t("{{count}} lots", { count: inputLots })}
            {" ▸ "}
            {formatUnit(inputQuantity, unit)}
          </h2>
          <Table
            style={{ width: "max(50vw, 960px)" }}
            rows={input}
            columns={compact([
              columns.supplier,
              columns.delivery,
              columns.biofuel,
              columns.quantity,
              pending ? columns.countWithPending : columns.count,
              columns.ghgReduction,
              pending && columns.shortcutInput,
            ])}
          />
        </>
      )}

      {output.length > 0 && (
        <>
          <h2>
            {t("Lots envoyés")}
            {" ▸ "}
            {t("{{count}} lots", { count: outputLots })}
            {" ▸ "}
            {formatUnit(outputQuantity, unit)}
          </h2>
          <Table
            rows={output}
            style={{ width: "max(50vw, 960px)" }}
            columns={compact([
              columns.client,
              columns.delivery,
              columns.biofuel,
              columns.quantity,
              pending ? columns.countWithPending : columns.count,
              columns.ghgReduction,
              pending && columns.shortcutOutput,
            ])}
          />
        </>
      )}

      {summary.loading && <LoaderOverlay />}
    </>
  )
}

export function useSummaryColumns(query: LotQuery) {
  const { t } = useTranslation()
  return {
    supplier: {
      key: "supplier",
      header: t("Fournisseur"),
      orderBy: (item: SummaryItem) => item.supplier ?? "",
      cell: (item: SummaryItem) => (
        <Cell text={item.supplier ?? t("Inconnu")} />
      ),
    },
    client: {
      key: "client",
      header: t("Client"),
      orderBy: (item: SummaryItem) => item.client ?? "",
      cell: (item: SummaryItem) => <Cell text={item.client ?? t("Inconnu")} />,
    },
    delivery: {
      key: "delivery",
      header: t("Livraison"),
      orderBy: (item: SummaryItem) => item.delivery_type ?? "",
      cell: (item: SummaryItem) => (
        <Cell text={getDeliveryLabel(item.delivery_type)} />
      ),
    },

    biofuel: {
      key: "biofuel",
      header: t("Biocarburant"),
      orderBy: (item: SummaryItem) =>
        t(item.biofuel_code ?? "", { ns: "biofuels" }) as string,
      cell: (item: SummaryItem) => (
        <Cell text={t(item.biofuel_code ?? "", { ns: "biofuels" })} />
      ),
    },
    volume: {
      key: "volume",
      header: t("Volume (litres)"),
      orderBy: (item: SummaryItem) => item.volume_sum,
      cell: (item: SummaryItem) => (
        <Cell text={formatNumber(item.volume_sum)} />
      ),
    },
    remainingVolume: {
      key: "remainingVolume",
      header: t("Volume restant (litres)"),
      orderBy: (item: SummaryItem) => item.remaining_volume_sum ?? 0,
      cell: (item: SummaryItem) => (
        <Cell text={formatNumber(item.remaining_volume_sum ?? 0)} />
      ),
    },
    quantity: {
      key: "volume",
      header: t("Quantité"),
      orderBy: (item: SummaryItem) => item.volume_sum,
      cell: (item: SummaryItem) => <QuantityCell item={item} />,
    },
    remainingQuantity: {
      key: "volume",
      header: t("Quantité restante"),
      orderBy: (item: SummaryItem) => item.remaining_volume_sum || 0,
      cell: (item: SummaryItem) => <RemainingQuantityCell item={item} />,
    },
    count: {
      small: true,
      key: "lots",
      header: t("Lots"),
      orderBy: (item: SummaryItem) => item.total,
      cell: (item: SummaryItem) => <Cell text={item.total} />,
    },
    countWithPending: {
      small: true,
      key: "validatedLots",
      header: t("Lots validés"),
      orderBy: (item: SummaryItem) => item.total - item.pending,
      cell: (item: SummaryItem) => <PendingCountCell item={item} />,
    },
    ghgReduction: {
      small: true,
      key: "ghg",
      header: t("Réd. GES"),
      orderBy: (item: SummaryItem) => item.avg_ghg_reduction || 0,
      cell: (item: SummaryItem) => (
        <Cell text={formatPercentage(item.avg_ghg_reduction || 0)} />
      ),
    },
    shortcutInput: {
      small: true,
      header: t("Aperçu"),
      cell: (item: SummaryItem) => (
        <PreviewCell status="in" item={item} query={query} />
      ),
    },
    shortcutOutput: {
      small: true,
      header: t("Aperçu"),
      cell: (item: SummaryItem) => (
        <PreviewCell status="out" item={item} query={query} />
      ),
    },
  }
}

interface SummaryCellProps {
  item: SummaryItem
}

export const PendingCountCell = ({ item }: SummaryCellProps) => (
  <p
    style={{
      color: item.pending > 0 ? "var(--orange-dark)" : undefined,
    }}
  >
    <strong>{item.total - item.pending}</strong>
    <small> / {item.total}</small>
  </p>
)

export const QuantityCell = ({ item }: SummaryCellProps) => {
  const entity = useEntity()

  const unitToField = {
    l: "volume_sum" as "volume_sum",
    kg: "weight_sum" as "weight_sum",
    MJ: "lhv_amount_sum" as "lhv_amount_sum",
  }

  const unit = entity.preferred_unit ?? "l"
  const field = unitToField[unit]

  return <Cell text={formatUnit(item[field] ?? 0, unit)} />
}

export const RemainingQuantityCell = ({ item }: SummaryCellProps) => {
  const entity = useEntity()

  const unitToField = {
    l: "remaining_volume_sum" as "remaining_volume_sum",
    kg: "remaining_weight_sum" as "remaining_weight_sum",
    MJ: "remaining_lhv_amount_sum" as "remaining_lhv_amount_sum",
  }

  const unit = entity.preferred_unit ?? "l"
  const field = unitToField[unit]

  return <Cell text={formatUnit(item[field] ?? 0, unit)} />
}

interface PreviewCellProps {
  status: "in" | "out"
  item: SummaryItem
  query: LotQuery
}

export const PreviewCell = ({ status, item, query }: PreviewCellProps) => {
  const { t } = useTranslation()

  const filters: Record<string, any> = {
    periods: query.periods,
    biofuels: [item.biofuel_code],
  }

  if (status === "in") {
    filters.suppliers = [item.supplier ?? "UNKNOWN"]
  } else {
    filters.clients = [item.client ?? "UNKNOWN"]
  }

  return (
    <ExternalLink
      href={`../../${query.year}/${status}/history?${toSearchParams(filters)}`}
    >
      {t("Voir")}
    </ExternalLink>
  )
}
