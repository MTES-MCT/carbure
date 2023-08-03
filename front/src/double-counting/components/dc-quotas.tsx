import { Trans, useTranslation } from "react-i18next"
import { useQuery } from "common/hooks/async"
import Table, { Cell, Column } from "common/components/table"
import { Dialog } from "common/components/dialog"
import { Button } from "common/components/button"
import { AlertCircle, Return } from "common/components/icons"
import { formatNumber } from "common/utils/formatters"
import { QuotaOverview, QuotaDetails, AgreementsSnapshot } from "../types"
import * as api from "../api"
import { usePortal } from "common/components/portal"
import Alert from "common/components/alert"
import { useState } from "react"
import { ActionBar } from "common/components/scaffold"
import Tabs from "common/components/tabs"


const QuotasList = ({ snapshot = defaultCount }: { snapshot: AgreementsSnapshot | undefined }) => {
  const { t } = useTranslation()
  const portal = usePortal()
  const year = new Date().getFullYear()
  const [tab, setTab] = useState("active")

  const quotas = useQuery(api.getQuotasSnapshot, {
    key: "dc-quotas-snapshot",
    params: [],
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
      <ActionBar>
        <Tabs
          focus={tab}
          variant="switcher"
          onFocus={setTab}
          tabs={[
            { key: "active", label: t("Actifs ({{count}})", { count: snapshot?.agreements_active }) },
            {
              key: "expired", label: t("Expirés ({{ count }})",
                { count: snapshot?.agreements_expired }
              )
            },
            {
              key: "incoming", label: t("À venir ({{ count }})",
                { count: snapshot?.agreements_incoming }
              )
            },
          ]}
        />

      </ActionBar>
      {quotaRows.length > 0 && (
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
      )}

      {quotaRows.length === 0 && (
        <Alert variant="warning" icon={AlertCircle} loading={quotas.loading}>
          {quotas.loading ?
            <Trans>Chargement en cours...</Trans>
            : <Trans>Aucun quota disponible</Trans>}

        </Alert>
      )}
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
            <Trans
              values={{ productionSite, producer, year }}
              defaults="Voici les détail de l'évolution des quotas pour le site de production <b>{{ productionSite }}</b> de <b>{{ producer }}</b> en <b>{{ year }}</b>"
            />
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

const defaultCount = {
  agreements_active: 0,
  agreements_expired: 0,
  agreements_incoming: 0
}
