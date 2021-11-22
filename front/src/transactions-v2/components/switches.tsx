import { Trans } from "react-i18next"
import endOfMonth from "date-fns/endOfMonth"
import { formatDeadline } from "common-v2/utils/formatters"
import { AlertCircle, Alarm } from "common-v2/components/icons"
import Switch, { SwitchProps } from "common-v2/components/switch"

export interface InvalidSwitchProps extends SwitchProps {
  count: number
}

export const InvalidSwitch = ({
  count,
  active,
  onSwitch,
}: InvalidSwitchProps) => (
  <Switch
    dismissable
    variant="danger"
    icon={AlertCircle}
    active={active}
    onSwitch={onSwitch}
  >
    <p>
      {!active && <Trans>Parmi ces résultats, </Trans>}
      <Trans count={count}>
        <b>{{ count }} lots</b> présentent des <b>incohérences</b>
      </Trans>
    </p>
  </Switch>
)

export interface DeadlineSwitchProps {
  count: number
  active: boolean
  onSwitch: (active: boolean) => void
}

export const DeadlineSwitch = ({
  count,
  active,
  onSwitch,
}: DeadlineSwitchProps) => {
  const deadline = getCurrentDeadline()
  const date = formatDeadline(deadline)

  return (
    <Switch
      dismissable
      variant="warning"
      icon={Alarm}
      active={active}
      onSwitch={onSwitch}
    >
      <p>
        {!active && <Trans>Parmi ces résultats, </Trans>}
        <Trans count={count}>
          <b>{{ count }} lots</b> doivent être déclarés avant le{" "}
          <b>{{ date }}</b>
        </Trans>
      </p>
    </Switch>
  )
}

export function getCurrentDeadline() {
  return endOfMonth(new Date())
}
