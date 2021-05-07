import cl from "clsx"

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
  errorCount,
  special,
}: InvalidFilterProps) => (
  <AlertFilter
    loading={loading}
    level="error"
    icon={AlertCircle}
    active={special.invalid}
    onActivate={() => special.setInvalid(true)}
    onDispose={() => special.setInvalid(false)}
  >
    {errorCount === 1 ? (
      <span>
        {!special.invalid && "Parmi ces résultats, "}
        <b>1 lot</b> présente des <b>incohérences</b>
      </span>
    ) : (
      <span>
        {!special.invalid && "Parmi ces résultats, "}
        <b>{errorCount} lots</b> présentent des <b>incohérences</b>
      </span>
    )}
  </AlertFilter>
)

type DeadlineFilterProps = {
  loading: boolean
  deadlineCount: number
  deadlineDate: string | null
  special: SpecialSelection
  entity: EntitySelection
}

export const DeadlineFilter = ({
  loading,
  deadlineCount,
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
    {deadlineCount === 1 ? (
      <span>
        {!special.deadline && "Parmi ces résultats, "}
        <b>1 lot</b> doit être{" "}
        {entity?.entity_type === "Opérateur" ? "accepté" : "validé et envoyé"}{" "}
        avant le <b>{deadlineDate}</b>
      </span>
    ) : (
      <span>
        {!special.deadline && "Parmi ces résultats, "}
        <b>{deadlineCount} lots</b> doivent être{" "}
        {entity?.entity_type === "Opérateur"
          ? "acceptés"
          : "validés et envoyés"}{" "}
        avant le <b>{deadlineDate ?? "N/A"}</b>
      </span>
    )}
  </AlertFilter>
)

type SummaryFilterProps = {
  loading: boolean
  txCount: number
  totalVolume: number
  query: TransactionQuery
  hideRecap?: boolean
  onReset: () => void
}

export const SummaryFilter = ({
  loading,
  txCount,
  totalVolume,
  query,
  hideRecap = false,
  onReset,
}: SummaryFilterProps) => {
  function showSummary() {
    prompt((resolve) => (
      <SummaryPrompt
        readOnly
        title="Récapitulatif de la recherche"
        description="Voici un résumé des lots correspondant aux filtres sélectionnés"
        query={query}
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
      {txCount === 1 ? (
        <span>
          <b>Un seul lot</b> a été trouvé, pour un total de{" "}
          <b>{prettyVolume(totalVolume)} litres</b>
        </span>
      ) : (
        <span>
          <b>{txCount} lots</b> ont été trouvés, pour un total de{" "}
          <b>{prettyVolume(totalVolume)} litres</b>
        </span>
      )}

      {!hideRecap && (
        <span className={styles.alertLink} onClick={showSummary}>
          Voir le récapitulatif
        </span>
      )}

      <span
        className={cl(styles.alertLink, styles.alertClose)}
        onClick={onReset}
      >
        Réinitialiser les filtres
      </span>
    </Alert>
  )
}
