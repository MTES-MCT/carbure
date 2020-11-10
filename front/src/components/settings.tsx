import React from "react"
import { EntitySelection } from "../hooks/helpers/use-entity"
import { SettingsGetter } from "../hooks/use-app"

import styles from "./settings.module.css"

import {
  enableMAC,
  disableMAC,
  disableTrading,
  enableTrading,
} from "../services/settings"
import useAPI from "../hooks/helpers/use-api"
import { Section, BoxProps, Title, LabelCheckbox } from "./system"

export const SettingsHeader = (props: BoxProps) => (
  <div className={styles.settingsTop}>
    <div {...props} className={styles.settingsHeader} />
  </div>
)

export const SettingsBody = (props: BoxProps) => (
  <div {...props} className={styles.settingsBody} />
)

type GeneralSettingsProps = {
  entity: EntitySelection
  settings: SettingsGetter
}

export const MACSettings = ({ entity, settings }: GeneralSettingsProps) => {
  const hasMAC: boolean = entity?.has_mac ?? false

  const [requestEnable, resolveMacEnabled] = useAPI(enableMAC)
  const [requestDisable, resolveMacDisabled] = useAPI(disableMAC)

  function onChangeMac(event: React.ChangeEvent<HTMLInputElement>): void {
    if (entity === null) {
      return
    }
    if (event.target.checked) {
      resolveMacEnabled(entity.id).then(settings.resolve)
    } else {
      resolveMacDisabled(entity.id).then(settings.resolve)
    }
  }

  if (entity === null) {
    return null
  }

  return (
    <Section>
      <Title>Mises à Consommation</Title>

      <LabelCheckbox
        label="Ma société effectue des Mises à Consommation"
        checked={hasMAC}
        onChange={onChangeMac}
      />
    </Section>
  )
}

export const TradingSettings = ({ entity, settings }: GeneralSettingsProps) => {
  const hasTrading: boolean = entity?.has_trading ?? false

  const [requestEnable, resolveTradingEnabled] = useAPI(enableTrading)
  const [requestDisable, resolveTradingDisabled] = useAPI(disableTrading)

  function onChangeTrading(event: React.ChangeEvent<HTMLInputElement>): void {
    if (entity === null) {
      return
    }

    if (event.target.checked) {
      resolveTradingEnabled(entity.id).then(settings.resolve)
    } else {
      resolveTradingDisabled(entity.id).then(settings.resolve)
    }
  }

  return (
    <Section>
      <Title>Trading</Title>

      <LabelCheckbox
        label="Ma société a une activité de négoce"
        checked={hasTrading}
        onChange={onChangeTrading}
      />
    </Section>
  )
}

type ProductionSitesSettingsProps = {}

export const ProductionSitesSettings = ({}: ProductionSitesSettingsProps) => (
  <Section>
    <Title>Sites de Production</Title>
  </Section>
)

type DeliverySitesSettingsProps = {}

export const DeliverySitesSettings = ({}: DeliverySitesSettingsProps) => (
  <Section>
    <Title>Dépôts</Title>
  </Section>
)
