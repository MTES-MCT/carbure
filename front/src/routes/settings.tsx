import React from "react"

import { EntitySelection } from "../hooks/helpers/use-entity"
import { SettingsGetter } from "../hooks/helpers/use-get-settings"

import { Main, Title } from "../components/system"
import {
  SettingsHeader,
  SettingsBody,
  MACSettings,
  TradingSettings,
  ProductionSitesSettings,
  DeliverySitesSettings,
} from "../components/settings"

type SettingsProps = {
  entity: EntitySelection
  settings: SettingsGetter
}

const Settings = ({ entity, settings }: SettingsProps) => {
  return (
    <Main>
      <SettingsHeader>
        <Title>Paramètres</Title>
      </SettingsHeader>

      <SettingsBody>
        <MACSettings entity={entity} settings={settings} />
        <TradingSettings entity={entity} settings={settings} />
        <ProductionSitesSettings />
        <DeliverySitesSettings />
      </SettingsBody>
    </Main>
  )
}
export default Settings
