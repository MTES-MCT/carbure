import React from "react"
import { SpecialSelection } from "../hooks/query/use-special"
import { AlertFilter } from "./system/alert"
import { AlertCircle, Calendar } from "./system/icons"

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
        <b>1 lot</b> présente des <b>incohérences</b>
      </span>
    ) : (
      <span>
        <b>{errorCount} lots</b> présentent des <b>incohérences</b>
      </span>
    )}
  </AlertFilter>
)

type DeadlineFilterProps = {
  deadlineCount: number
  deadlineDate: string | null
  special: SpecialSelection
}

export const DeadlineFilter = ({
  deadlineCount,
  deadlineDate,
  special,
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
        <b>1 lot</b> doit être validé et envoyé avant le <b>{deadlineDate}</b>
      </span>
    ) : (
      <span>
        <b>{deadlineCount} lots</b> doivent être validés et envoyés avant le{" "}
        <b>{deadlineDate ?? "N/A"}</b>
      </span>
    )}
  </AlertFilter>
)
