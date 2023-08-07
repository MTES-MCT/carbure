import { Trans, useTranslation } from "react-i18next"
import { useQuery } from "common/hooks/async"
import Table, { Cell, Column } from "common/components/table"
import { Dialog } from "common/components/dialog"
import { Button } from "common/components/button"
import { AlertCircle, Return } from "common/components/icons"
import { formatDateYear, formatNumber } from "common/utils/formatters"
import { AgreementOverview, QuotaDetails, AgreementsSnapshot, AgreementStatus } from "../types"
import * as api from "../api"
import { usePortal } from "common/components/portal"
import Alert from "common/components/alert"
import { useState } from "react"
import { ActionBar, LoaderOverlay } from "common/components/scaffold"
import Tabs from "common/components/tabs"
import Tag, { TagVariant } from "common/components/tag"
import AgreementStatusTag from "./agreement-status"


type AgreementDetailsDialogProps = {
  year: number
  quota: AgreementOverview
  onClose: () => void
}

const AgreementDetailsDialog = ({
  year,
  quota,
  onClose,
}: AgreementDetailsDialogProps) => {
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

export default AgreementDetailsDialog

