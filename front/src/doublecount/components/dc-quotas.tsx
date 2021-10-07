
import { Fragment, useState, useEffect } from "react"
import { useTranslation, Trans } from "react-i18next"
import { DoubleCounting } from "common/types"
import { LoaderOverlay } from "common/components"
import Tabs from "common/components/tabs"
import Table, { Column } from "common/components/table"
import { padding } from "transactions/components/list-columns"
import { Alert } from "common/components/alert"
import { AlertCircle } from "common/components/icons"
import { formatDate, YEAR_ONLY } from "settings/components/common"
import { DoubleCountingPrompt } from "./agreement-details"
import { EntitySelection } from "carbure/hooks/use-entity"
import useAPI from "common/hooks/use-api"
import {
  Dialog,
  DialogButtons,
  DialogTitle,
  DialogText,
  prompt,
  PromptProps,
} from "common/components/dialog"
import DoubleCountingStatus from './dc-status'
import * as api from "../api"

type QuotasDetailsPromptProps = PromptProps<void> & {
  quota: api.QuotaOverview
}

const QuotasDetailsPrompt = ({ onResolve, quota, ...props }: QuotasDetailsPromptProps) => {
  const { t } = useTranslation()
  
  const columns: Column<api.QuotaOverview>[] = [
    padding,
    { header: t("Producteur"), render: (a) => a.producer.name },
    { header: t("Site de production"), render: (a) => a.production_site.name },
    { header: t("Progression des quotas"), render: (a) => <progress value={a.current_production_weight_sum} max={a.approved_quota_weight_sum} /> },
    { header: t("Quotas remplis"), render: (a) => <span>{a.nb_full_quotas + a.nb_breached_quotas} / {a.nb_quotas}</span> },
    { header: t("Quotas dépassés"), render: (a) => <span>{a.nb_breached_quotas}</span> },
    padding,
  ]

  return (
    <Dialog onResolve={onResolve}>
      <DialogTitle text={t("Détails des quotas")} />

      <Table
        columns={columns}
        rows={[]}
      />
    </Dialog>
  )
}

type QuotasListProps = {
  entity: EntitySelection
  year: number
}

const QuotasList = ({ entity, year }: QuotasListProps) => {
  const { t } = useTranslation()

  const [quotas, getQuotas] = useAPI(api.getQuotasSnapshot)

  useEffect(() => {
    getQuotas(year)
  }, [getQuotas, year])

  const columns: Column<api.QuotaOverview>[] = [
    padding,
    { header: t("Producteur"), render: (a) => a.producer.name },
    { header: t("Site de production"), render: (a) => a.production_site.name },
    { header: t("Progression des quotas"), render: (a) => <progress value={a.current_production_weight_sum} max={a.approved_quota_weight_sum} /> },
    { header: t("Quotas remplis"), render: (a) => <span>{a.nb_full_quotas + a.nb_breached_quotas} / {a.nb_quotas}</span> },
    { header: t("Quotas dépassés"), render: (a) => <span>{a.nb_breached_quotas}</span> },
    padding,
  ]

  const quotaRows = (quotas.data ?? []).map((quota) => ({
    value: quota,
    onClick: () => prompt((resolve) => (
      <QuotasDetailsPrompt quota={quota} onResolve={resolve} />
    ))
  }))

  return (
    <Fragment>
      <Table
        columns={columns}
        rows={quotaRows}
      />

      {quotas.loading && <LoaderOverlay />}
    </Fragment>
  )
}

export default QuotasList
