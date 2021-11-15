import { Trans, useTranslation } from "react-i18next"
import { AlertCircle, Alarm, Wrench } from "common-v2/components/icons"
import Switch, { SwitchProps } from "common-v2/components/switch"
import Tabs from "common-v2/components/tabs"

export interface HistorySwitcherProps {
  focus: string
  pending: number
  history: number
  pendingLabel?: string
  historyLabel?: string
  onFocus: (sub: string) => void
}

export const HistorySwitcher = ({
  focus,
  pending,
  history,
  pendingLabel,
  historyLabel,
  onFocus: onSwitch,
}: HistorySwitcherProps) => {
  const { t } = useTranslation()
  return (
    <Tabs
      variant="switcher"
      focus={focus}
      onFocus={onSwitch}
      tabs={[
        {
          key: "pending",
          label: `${pendingLabel ?? t("En attente")} (${pending})`,
        },
        {
          key: "history",
          label: `${historyLabel ?? t("Historique")} (${history})`,
        },
      ]}
    />
  )
}

export interface CorrectionSwitchProps extends SwitchProps {
  count: number
}

export const CorrectionSwitch = ({
  count,
  active,
  onSwitch,
}: CorrectionSwitchProps) => (
  <Switch
    dismissable
    variant="warning"
    icon={Wrench}
    active={active}
    onSwitch={onSwitch}
  >
    <p>
      {!active && <Trans>Parmi ces résultats, </Trans>}
      <Trans count={count}>
        <b>{{ count }} lots</b> sont en attente de correction.
      </Trans>
    </p>
  </Switch>
)

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
  date: string
  active: boolean
  onSwitch: (active: boolean) => void
}

export const DeadlineSwitch = ({
  count,
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
      <Trans count={count}>
        <b>{{ count }} lots</b> doivent être déclarés avant le <b>{{ date }}</b>
      </Trans>
    </p>
  </Switch>
)
