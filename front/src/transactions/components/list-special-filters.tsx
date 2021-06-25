import cl from "clsx"
import { Trans, useTranslation } from "react-i18next"

import { EntitySelection } from "carbure/hooks/use-entity"
import { SpecialSelection } from "transactions/hooks/query/use-special"
import { Alert, AlertFilter } from "common/components/alert"
import { Alarm, AlertCircle, Filter, Loader } from "common/components/icons"

import styles from "common/components/alert.module.css"
import { prettyVolume } from "transactions/helpers"
import { TransactionQuery } from "common/types"
import { prompt } from "common/components/dialog"
import { SummaryPrompt } from "./summary"

type InvalidFilterProps = {
  loading: boolean
  errorCount: number
  special: SpecialSelection
}

export const InvalidFilter = ({
  loading,
  errorCount: count,
  special,
}: InvalidFilterProps) => {
  return (
    <AlertFilter
      loading={loading}
      level="error"
      icon={AlertCircle}
      active={special.invalid}
      onActivate={() => special.setInvalid(true)}
      onDispose={() => special.setInvalid(false)}
    >
      <span>
        {!special.invalid && <Trans>Parmi ces résultats, </Trans>}
        <Trans count={count}>
          <b>{{ count }} lots</b> présentent des <b>incohérences</b>
        </Trans>
      </span>
    </AlertFilter>
  )
}

type DeadlineFilterProps = {
  loading: boolean
  deadlineCount: number
  deadlineDate: string | null
  special: SpecialSelection
  entity: EntitySelection
}

export const DeadlineFilter = ({
  loading,
  deadlineCount: count,
  deadlineDate,
  special,
  entity,
}: DeadlineFilterProps) => (
  <AlertFilter
    loading={loading}
    level="warning"
    icon={Alarm}
    active={special.deadline}
    onActivate={() => special.setDeadline(true)}
    onDispose={() => special.setDeadline(false)}
  >
    <span>
      {!special.deadline && <Trans>Parmi ces résultats, </Trans>}
      <Trans count={count}>
        <b>{{ count }} lots</b> doivent être déclarés avant le{" "}
        <b>{{ date: deadlineDate ?? "N/A" }}</b>
      </Trans>
    </span>
  </AlertFilter>
)

type SummaryFilterProps = {
  loading: boolean
  txCount: number
  filterCount: number
  totalVolume: number
  query: TransactionQuery
  hideRecap?: boolean
  selection: number[]
  entity: EntitySelection
  stock?: boolean
  onReset: () => void
}

export const SummaryFilter = ({
  loading,
  txCount: count,
  filterCount,
  totalVolume,
  query,
  selection,
  hideRecap = false,
  entity,
  stock = false,
  onReset,
}: SummaryFilterProps) => {
  const { t } = useTranslation()

  function showSummary() {
    prompt((resolve) => (
      <SummaryPrompt
        readOnly
        stock={stock}
        title={t("Récapitulatif des lots")}
        description={t(
          "Ce tableau résume les informations principales des lots correspondant à votre recherche ou sélection."
        )}
        query={query}
        entity={entity}
        selection={selection}
        onResolve={resolve}
      />
    ))
  }

  return (
    <Alert
      level="info"
      icon={loading ? Loader : Filter}
      className={cl(styles.alertFilter, loading && styles.alertLoading)}
    >
      <span>
        <Trans count={count}>
          <b>{{ count }} lots</b> pour un total de{" "}
          <b>{{ volume: prettyVolume(totalVolume) }} litres</b>
        </Trans>
      </span>

      {!hideRecap && (
        <span className={styles.alertLink} onClick={showSummary}>
          <Trans>Voir le récapitulatif</Trans>
        </span>
      )}

      <span
        className={cl(styles.alertLink, styles.alertClose)}
        onClick={onReset}
      >
        <Trans>Réinitialiser les filtres</Trans>
      </span>
      <span className={styles.alertExtra}>({filterCount})</span>
    </Alert>
  )
}

type NoResultProps = {
  loading: boolean
  filterCount: number
  onReset: () => void
}

export const NoResult = ({ loading, filterCount, onReset }: NoResultProps) => (
  <Alert
    level="warning"
    icon={loading ? Loader : AlertCircle}
    className={cl(styles.alertFilter, loading && styles.alertLoading)}
  >
    <Trans>Aucune transaction trouvée pour cette recherche</Trans>

    <span className={cl(styles.alertLink, styles.alertClose)} onClick={onReset}>
      <Trans>Réinitialiser les filtres</Trans>
    </span>
    <span className={styles.alertExtra}>({filterCount})</span>
  </Alert>
)
