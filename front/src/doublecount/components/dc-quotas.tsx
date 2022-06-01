import { Fragment } from "react"
import { Trans, useTranslation } from "react-i18next"
import { useQuery } from "common-v2/hooks/async"
import { LoaderOverlay } from "common-v2/components/scaffold"
import Table, { Cell, Column } from "common-v2/components/table"
import { Dialog } from "common-v2/components/dialog"
import { Button } from "common-v2/components/button"
import { Return } from "common-v2/components/icons"
import { formatNumber } from "common-v2/utils/formatters"
import { QuotaOverview, QuotaDetails } from "../types"
import * as api from "../api"
import { usePortal } from "common-v2/components/portal"

type QuotasListProps = {
  year: number
}

const QuotasList = ({ year }: QuotasListProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  const quotas = useQuery(api.getQuotasSnapshot, {
    key: "dc-quotas-snapshot",
    params: [year],
  })

  const columns: Column<QuotaOverview>[] = [
    { header: t("Producteur"), cell: (a) => <Cell text={a.producer.name} /> },
    {
      header: t("Site de production"),
      cell: (a) => <Cell text={a.production_site.name} />,
    },
    {
      header: t("Quotas remplis"),
      cell: (a) => (
        <span>
          {a.nb_full_quotas + a.nb_breached_quotas} / {a.nb_quotas}
        </span>
      ),
    },
    {
      header: t("Quotas dépassés"),
      cell: (a) => <span>{a.nb_breached_quotas}</span>,
    },
    {
      header: t("Progression des quotas"),
      cell: (a) => (
        <progress
          value={a.current_production_weight_sum}
          max={a.approved_quota_weight_sum}
          title={`${a.current_production_weight_sum} / ${a.approved_quota_weight_sum}`}
        />
      ),
    },
  ]

  const quotaRows = quotas.result?.data.data ?? []

  return (
    <section>
      <Table
        loading={quotas.loading}
        columns={columns}
        rows={quotaRows}
        onAction={(quota) =>
          portal((close) => (
            <QuotasDetailsDialog year={year} quota={quota} onClose={close} />
          ))
        }
      />
    </section>
  )
}

type QuotasDetailsDialogProps = {
  year: number
  quota: QuotaOverview
  onClose: () => void
}

const QuotasDetailsDialog = ({
  year,
  quota,
  onClose,
}: QuotasDetailsDialogProps) => {
  const { t } = useTranslation()
  const quotaDetails = useQuery(api.getQuotaDetails, {
    key: "dc-quota-details",
    params: [year, quota.production_site.id],
  })

  const columns: Column<QuotaDetails>[] = [
    {
      header: t("Biocarburant"),
      cell: (d) => <Cell text={d.biofuel.name} />,
    },
    {
      header: t("Matière première"),
      cell: (d) => <Cell text={d.feedstock.name} />,
    },
    { header: t("Nombre de lots"), cell: (d) => <Cell text={d.nb_lots} /> },
    {
      header: t("Volume produit"),
      cell: (d) => (
        <Cell
          text={`${formatNumber(d.volume)} L`}
          sub={`${d.current_production_weight_sum_tonnes} t`}
        />
      ),
    },
    {
      header: t("Quota approuvé"),
      cell: (d) => <Cell text={formatNumber(d.approved_quota)} />,
    },
    {
      header: t("Progression des quotas"),
      cell: (d) => (
        <progress
          max={d.approved_quota}
          value={d.current_production_weight_sum_tonnes}
          title={`${d.current_production_weight_sum_tonnes} / ${d.approved_quota}`}
        />
      ),
    },
  ]

  const producer = quota.producer.name
  const productionSite = quota.production_site.name

  const rows = quotaDetails.result?.data.data ?? []

  return (
    <Dialog fullscreen onClose={onClose}>
      <header>
        <h1>{t("Détails des quotas")}</h1>
      </header>

      <main>
        <section>
          <p>
            <Trans>
              Voici les détail de l'évolution des quotas pour le site de
              production <b>{{ productionSite }}</b> de <b>{{ producer }}</b> en{" "}
              <b>{{ year }}</b>
            </Trans>
          </p>
        </section>

        <Table loading={quotaDetails.loading} columns={columns} rows={rows} />
      </main>

      <footer>
        <Button asideX icon={Return} action={onClose} label={t("Retour")} />
      </footer>
    </Dialog>
  )
}

export default QuotasList
