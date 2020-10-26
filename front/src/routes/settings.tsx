import React from "react"

import { EntitySelection } from "../hooks/helpers/use-entity"
import { SettingsGetter } from "../hooks/helpers/use-get-settings"

import styles from "../components/settings.module.css"

import { Main, Box, Title } from "../components/system"
import {
  GeneralSettings,
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
      <Box className={styles.settingsTop}>
        <div className={styles.settingsHeader}>
          <Title>Paramètres</Title>
        </div>
      </Box>
      <GeneralSettings entity={entity} settings={settings} />
      <ProductionSitesSettings data={0} />
      <DeliverySitesSettings data={0} />
    </Main>
  )
}
export default Settings
