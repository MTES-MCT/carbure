import { Fragment, useEffect } from "react"
import { Trans, useTranslation } from "react-i18next"
import { LoaderOverlay } from "common/components"
import Table, { Column } from "common/components/table"
import { padding } from "transactions/components/list-columns"
import useAPI from "common/hooks/use-api"
import {
  Dialog,
  DialogButtons,
  DialogTitle,
  DialogText,
  DialogTable,
  prompt,
  PromptProps,
} from "common/components/dialog"
import * as api from "../api"
import { Button } from "common/components/button"
import { Return } from "common/components/icons"

type QuotasDetailsPromptProps = PromptProps<void> & {
  year: number
  quota: api.QuotaOverview
}

const QuotasDetailsPrompt = ({
  year,
  quota,
  onResolve,
}: QuotasDetailsPromptProps) => {
  const { t } = useTranslation()
  const [details, getDetails] = useAPI(api.getQuotaDetails)

  useEffect(() => {
    getDetails()
  }, [getDetails])

  const columns: Column<api.QuotaDetails>[] = [
    padding,
    { header: t("Biocarburant"), render: (d) => "" },
    { header: t("Matière première"), render: (d) => "" },
    {
      header: t("Progression des quotas"),
      render: (d) => <progress />,
    },
    padding,
  ]

  const producer = quota.producer.name
  const productionSite = quota.production_site.name

  const rows = (details.data ?? []).map((value) => ({ value }))

  return (
    <Dialog onResolve={onResolve}>
      <DialogTitle text={t("Détails des quotas")} />

      <DialogText>
        <Trans>
          Voici les détail de l'évolution des quotas pour le site de production{" "}
          <b>{{ productionSite }}</b> de <b>{{ producer }}</b> en{" "}
          <b>{{ year }}</b>
        </Trans>
      </DialogText>

      <DialogTable columns={columns} rows={rows} />

      <DialogButtons>
        <Button icon={Return} onClick={() => onResolve()}>
          <Trans>Retour</Trans>
        </Button>
      </DialogButtons>
    </Dialog>
  )
}

type QuotasListProps = {
  year: number
}

const QuotasList = ({ year }: QuotasListProps) => {
  const { t } = useTranslation()

  const [quotas, getQuotas] = useAPI(api.getQuotasSnapshot)

  useEffect(() => {
    getQuotas(year)
  }, [getQuotas, year])

  const columns: Column<api.QuotaOverview>[] = [
    padding,
    { header: t("Producteur"), render: (a) => a.producer.name },
    { header: t("Site de production"), render: (a) => a.production_site.name },
    {
      header: t("Progression des quotas"),
      render: (a) => (
        <progress
          value={a.current_production_weight_sum}
          max={a.approved_quota_weight_sum}
          title={`${a.current_production_weight_sum} / ${a.approved_quota_weight_sum}`}
        />
      ),
    },
    {
      header: t("Quotas remplis"),
      render: (a) => (
        <span>
          {a.nb_full_quotas + a.nb_breached_quotas} / {a.nb_quotas}
        </span>
      ),
    },
    {
      header: t("Quotas dépassés"),
      render: (a) => <span>{a.nb_breached_quotas}</span>,
    },
    padding,
  ]

  const quotaRows = (quotas.data ?? []).map((quota) => ({
    value: quota,
    onClick: () =>
      prompt((resolve) => (
        <QuotasDetailsPrompt year={year} quota={quota} onResolve={resolve} />
      )),
  }))

  return (
    <Fragment>
      <Table columns={columns} rows={quotaRows} />

      {quotas.loading && <LoaderOverlay />}
    </Fragment>
  )
}

export default QuotasList
