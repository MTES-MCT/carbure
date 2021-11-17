import { Trans, useTranslation } from "react-i18next"
import { useQuery } from "common-v2/hooks/async"
import * as api from "../api"
import Alert from "common-v2/components/alert"
import Button from "common-v2/components/button"
import Dialog from "common-v2/components/dialog"
import Table, { Cell, Column } from "common-v2/components/table"
import { Filter, Loader, Return } from "common-v2/components/icons"
import { formatNumber, formatPercentage } from "common-v2/utils/formatters"
import { LotQuery } from "../hooks/lot-query"
import { LotSummary, LotSummaryItem } from "../types"
import { FilterManager } from "./filters"
import { ResetButton } from "./no-result"
import { LoaderOverlay } from "common-v2/components/scaffold"
import { usePortal } from "common-v2/components/portal"

export interface SummaryBarProps {
  query: LotQuery
  selection: number[]
  filters: FilterManager
}

export const Summary = ({ query, selection, filters }: SummaryBarProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  const summary = useQuery(api.getLotsSummary, {
    key: "lots-summary",
    params: [query, selection, true],
  })

  const summaryData = summary.result?.data.data

  if (!summaryData) return null

  return (
    <Alert icon={summary.loading ? Loader : Filter} variant="info">
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
            <SummaryDialog
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

export interface SummaryDialogProps {
  query: LotQuery
  selection: number[]
  onClose: () => void
}

export const SummaryDialog = ({
  query,
  selection,
  onClose,
}: SummaryDialogProps) => {
  const { t } = useTranslation()

  const summary = useQuery(api.getLotsSummary, {
    key: "lots-summary-details",
    params: [query, selection],
  })

  const summaryData = summary.result?.data.data

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

        {summaryData && <SummaryTable summary={summaryData} />}
      </main>

      <footer>
        <Button asideX icon={Return} label={t("Retour")} action={onClose} />
      </footer>

      {summary.loading && <LoaderOverlay />}
    </Dialog>
  )
}

export interface SummaryTableProps {
  summary: LotSummary
}

export const SummaryTable = ({ summary }: SummaryTableProps) => {
  const { t } = useTranslation()

  const columns: Column<LotSummaryItem>[] = [
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
      key: "lots",
      header: t("Lots"),
      orderBy: (item) => item.count,
      cell: (item) => <Cell text={formatNumber(item.count)} />,
    },
    {
      key: "ghg",
      header: t("Moy. Réd. GES"),
      orderBy: (item) => item.avg_ghg_reduction,
      cell: (item) => <Cell text={formatPercentage(item.avg_ghg_reduction)} />,
    },
  ]

  const input = summary.in ?? []
  const inputLots = input.reduce((count, item) => count + item.count, 0)
  const inputVolume = input.reduce((volume, item) => volume + item.volume_sum, 0) // prettier-ignore

  const output = summary.out ?? []
  const outputLots = output.reduce((count, item) => count + item.count, 0)
  const outputVolume = output.reduce((volume, item) => volume + item.volume_sum, 0) // prettier-ignore

  return (
    <>
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
    </>
  )
}

export default Summary
