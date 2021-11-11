import { Trans } from "react-i18next"
import { AlertCircle, Alarm } from "common-v2/components/icons"
import Switch, { SwitchProps } from "common-v2/components/switch"

export interface InvalidSwitchProps extends SwitchProps {
  total: number
}

export const InvalidSwitch = ({
  total,
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
      <Trans count={total}>
        <b>{{ total }} lots</b> présentent des <b>incohérences</b>
      </Trans>
    </p>
  </Switch>
)

export interface DeadlineSwitchProps {
  total: number
  date: string
  active: boolean
  onSwitch: (active: boolean) => void
}

export const DeadlineSwitch = ({
  total,
  date,
  active,
  onSwitch,
}: DeadlineSwitchProps) => (
  <Switch
    dismissable
    variant="warning"
    icon={Alarm}
    active={active}
    onSwitch={onSwitch}
  >
    <p>
      {!active && <Trans>Parmi ces résultats, </Trans>}
      <Trans count={total}>
        <b>{{ count: total }} lots</b> doivent être déclarés avant le{" "}
        <b>{{ deadline: date }}</b>
      </Trans>
    </p>
  </Switch>
)
