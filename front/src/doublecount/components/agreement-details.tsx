import { useState, useEffect } from 'react'
import { useTranslation, Trans } from 'react-i18next'
import { DoubleCountingStatus, DoubleCountingSourcing, DoubleCountingProduction } from 'common/types'
import useAPI from 'common/hooks/use-api'
import { LoaderOverlay, Box } from 'common/components'
import Tabs from 'common/components/tabs'
import { Button } from 'common/components/button'
import Table, { Column, Row } from 'common/components/table'
import { padding } from 'transactions/components/list-columns'
import * as api from '../api'
import {
  Dialog,
  DialogButtons,
  DialogTitle,
  prompt,
  PromptProps,
} from "common/components/dialog"
import { useEntityContext, EntitySelection } from 'carbure/hooks/use-entity'
import { DCStatus } from 'settings/components/double-counting'
import styles from "settings/components/settings.module.css"
import { Return } from 'common/components/icons'

export type DoubleCountingPromptProps = PromptProps<any> & {
  agreementID: number
}

export const DoubleCountingPrompt = ({
  agreementID,
  onResolve,
}: DoubleCountingPromptProps) => {
  const { t } = useTranslation()
  const entity = useEntityContext()

  const [focus, setFocus] = useState("sourcing")

  const [agreement, getAgreement] = useAPI(api.getDoubleCountingAgreement)
  const dcaStatus = agreement.data?.status ?? DoubleCountingStatus.Pending

  useEffect(() => {
      getAgreement(agreementID)
  }, [agreementID, getAgreement])

  const sourcingColumns: Column<DoubleCountingSourcing>[] = [
    padding,
    {
      header: t("Année"),
      render: (s) => s.year,
    },
    {
      header: t("Matière première"),
      render: (s) => t(s.feedstock.code, { ns: "feedstocks" }),
    },
    {
      header: t("Poids en tonnes"),
      render: (s) => s.metric_tonnes,
    },
    {
      header: t("Origine"),
      render: (s) => t(s.origin_country.code_pays, { ns: "countries" }),
    },
    {
      header: t("Approvisionnement"),
      render: (s) =>
        s.supply_country && t(s.supply_country.code_pays, { ns: "countries" }),
    },
    {
      header: t("Transit"),
      render: (s) =>
        s.transit_country &&
        t(s.transit_country.code_pays, { ns: "countries" }),
    },
    padding,
  ]

  const sourcingRows: Row<DoubleCountingSourcing>[] = (
    agreement.data?.sourcing ?? []
  ).map((s) => ({ value: s }))

  const productionColumns: Column<DoubleCountingProduction>[] = [
    padding,
    {
      header: t("Année"),
      render: (p) => p.year,
    },
    {
      header: t("Matière première"),
      render: (p) => t(p.feedstock.code, { ns: "feedstocks" }),
    },
    {
      header: t("Biocarburant"),
      render: (p) => t(p.biofuel.code, { ns: "biofuels" }),
    },
    {
      header: t("Prod. max"),
      render: (p) => p.max_production_capacity,
    },
    {
      header: t("Prod. estimée"),
      render: (p) => p.estimated_production,
    },
    {
      header: t("Quota demandé"),
      render: (p) => p.requested_quota,
    },
    {
      header: t("Quota approuvé"),
      render: (p) => p.approved_quota,
    },
    padding,
  ]

  const productionRows: Row<DoubleCountingProduction>[] = (
    agreement.data?.production ?? []
  ).map((p) => ({ value: p }))

  return (
    <Dialog wide onResolve={onResolve} className={styles.settingsPrompt}>
      <Box row>
        <DCStatus status={dcaStatus} />
        <DialogTitle text={t("Dossier double comptage")} />
      </Box>

      <Tabs
        tabs={[
          { key: "sourcing", label: t("Approvisionnement") },
          { key: "production", label: t("Production") },
        ]}
        focus={focus}
        onFocus={setFocus}
      />

      {focus === "sourcing" && (
        <div className={styles.modalTableContainer}>
          <Table columns={sourcingColumns} rows={sourcingRows} />
        </div>
      )}

      {focus === "production" && (
        <div className={styles.modalTableContainer}>
          <Table columns={productionColumns} rows={productionRows} />
        </div>
      )}

      <DialogButtons>
        <Button icon={Return} onClick={() => onResolve()}>
          <Trans>Retour</Trans>
        </Button>
      </DialogButtons>

      {agreement.loading && <LoaderOverlay />}
    </Dialog>
  )
}