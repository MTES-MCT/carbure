import { EntitySelection } from "carbure/hooks/use-entity"
import { SpecialSelection } from "transactions/hooks/query/use-special"
import { AlertFilter } from "common/components/alert"
import { AlertCircle, Calendar } from "common/components/icons"

type InvalidFilterProps = {
  errorCount: number
  special: SpecialSelection
}

export const InvalidFilter = ({ errorCount, special }: InvalidFilterProps) => (
  <AlertFilter
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
  deadlineCount: number
  deadlineDate: string | null
  special: SpecialSelection
  entity: EntitySelection
}

export const DeadlineFilter = ({
  deadlineCount,
  deadlineDate,
  special,
  entity,
}: DeadlineFilterProps) => (
  <AlertFilter
    level="warning"
    icon={Calendar}
    active={special.deadline}
    onActivate={() => special.setDeadline(true)}
    onDispose={() => special.setDeadline(false)}
  >
    {deadlineCount === 1 ? (
      <span>
        {!special.deadline && "Parmi ces résultats, "}
        <b>1 lot</b> doit être{" "}
        {entity?.entity_type === "Opérateur" && "accepté"}{" "}
        {entity?.entity_type !== "Opérateur" && "validé et envoyé"} avant le{" "}
        <b>{deadlineDate}</b>
      </span>
    ) : (
      <span>
        {!special.deadline && "Parmi ces résultats, "}
        <b>{deadlineCount} lots</b> doivent être{" "}
        {entity?.entity_type === "Opérateur" && "acceptés"}{" "}
        {entity?.entity_type !== "Opérateur" && "validés et envoyés"} avant le{" "}
        <b>{deadlineDate ?? "N/A"}</b>
      </span>
    )}
  </AlertFilter>
)
