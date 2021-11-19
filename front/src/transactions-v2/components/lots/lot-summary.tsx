import { Trans, useTranslation } from "react-i18next"
import { useQuery } from "common-v2/hooks/async"
import * as api from "../../api"
import { LotQuery, SummaryItem } from "../../types"
import { formatNumber, formatPercentage } from "common-v2/utils/formatters"
import { usePortal } from "common-v2/components/portal"
import { LoaderOverlay } from "common-v2/components/scaffold"
import Alert from "common-v2/components/alert"
import Button from "common-v2/components/button"
import Dialog from "common-v2/components/dialog"
import Table, { Cell, Column } from "common-v2/components/table"
import { Filter, Return } from "common-v2/components/icons"
import { FilterManager, ResetButton } from "../filters"
import NoResult from "../no-result"

export interface LotSummaryBarProps {
  query: LotQuery
  selection: number[]
  filters: FilterManager
}

export const LotSummaryBar = ({
  query,
  selection,
  filters,
}: LotSummaryBarProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  const summary = useQuery(api.getLotsSummary, {
    key: "lots-summary",
    params: [query, selection, true],
  })

  const summaryData = summary.result?.data.data ?? { count: 0, total_volume: 0 }

  return (
    <Alert loading={summary.loading} icon={Filter} variant="info">
      <p>
        <Trans count={summaryData.count}>
          <b>{{ count: formatNumber(summaryData.count) }} lots</b> pour un total
          de <b>{{ volume: formatNumber(summaryData.total_volume) }} litres</b>
        </Trans>
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
            />
          ))
        }
      />

      <ResetButton filters={filters} />
    </Alert>
  )
}

export interface LotSummaryDialogProps {
  query: LotQuery
  selection: number[]
  onClose: () => void
}

export const LotSummaryDialog = ({
  query,
  selection,
  onClose,
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

        <LotSummary query={query} selection={selection} />
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
}

const EMPTY: number[] = []

export const LotSummary = ({
  pending,
  query,
  selection = EMPTY,
}: LotSummaryProps) => {
  const { t } = useTranslation()

  const summary = useQuery(api.getLotsSummary, {
    key: "lots-summary-details",
    params: [query, selection],
  })

  const columns: Column<SummaryItem>[] = [
    {
      key: "biofuel",
      header: t("Biocarburant"),
      orderBy: (item) => item.biofuel_code,
      cell: (item) => <Cell text={t(item.biofuel_code, { ns: "biofuels" })} />,
    },
    {
      key: "volume",
      header: t("Volume (litres)"),
      orderBy: (item) => item.volume_sum,
      cell: (item) => <Cell text={formatNumber(item.volume_sum)} />,
    },
    {
      small: true,
      key: "lots",
      header: pending ? t("Lots validés") : t("Lots"),
      orderBy: (item) => item.total,
      cell: (item) => <LotCell pending={pending} item={item} />,
    },
    {
      small: true,
      key: "ghg",
      header: t("Réd. GES"),
      orderBy: (item) => item.avg_ghg_reduction,
      cell: (item) => <Cell text={formatPercentage(item.avg_ghg_reduction)} />,
    },
  ]

  const summaryData = summary.result?.data.data

  const input = summaryData?.in ?? []
  const inputLots = input.reduce((count, item) => count + item.total, 0)
  const inputVolume = input.reduce((volume, item) => volume + item.volume_sum, 0) // prettier-ignore

  const output = summaryData?.out ?? []
  const outputLots = output.reduce((count, item) => count + item.total, 0)
  const outputVolume = output.reduce((volume, item) => volume + item.volume_sum, 0) // prettier-ignore

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
            <Trans>
              Entrées ▸ {{ lots: formatNumber(inputLots) }} lots ▸{" "}
              {{ volume: formatNumber(inputVolume) }} litres
            </Trans>
          </h2>
          <Table
            rows={input}
            columns={[
              {
                key: "supplier",
                header: t("Fournisseur"),
                orderBy: (item) => item.supplier ?? "",
                cell: (item) => <Cell text={item.supplier ?? t("Inconnu")} />,
              },
              ...columns,
            ]}
          />
        </>
      )}

      {output.length > 0 && (
        <>
          <h2>
            <Trans>
              Sorties ▸ {{ lots: formatNumber(outputLots) }} lots ▸{" "}
              {{ volume: formatNumber(outputVolume) }} litres
            </Trans>
          </h2>
          <Table
            rows={output}
            columns={[
              {
                key: "client",
                header: t("Client"),
                orderBy: (item) => item.client ?? "",
                cell: (item) => <Cell text={item.client ?? t("Inconnu")} />,
              },
              ...columns,
            ]}
          />
        </>
      )}

      {summary.loading && <LoaderOverlay />}
    </>
  )
}

interface LotCellProps {
  pending?: boolean
  item: SummaryItem
}

export const LotCell = ({ pending, item }: LotCellProps) => {
  if (!pending) return <Cell text={item.total} />

  return (
    <p
      style={{
        color: item.pending > 0 ? "var(--orange-dark)" : undefined,
      }}
    >
      <strong>{item.total - item.pending}</strong>
      <small> / {item.total}</small>
    </p>
  )
}
