import React from "react"

import { Main, Box, Title } from "../components/system"
import { GeneralSettings, ProductionSitesSettings, DeliverySitesSettings } from "../components/settings"
import { EntitySelection } from "../hooks/helpers/use-entity"
import useSettings from "../hooks/settings/use-settings"

import styles from "../components/settings.module.css"

type SettingsProps = {
  entity: EntitySelection
}

const Settings = ({ entity }: SettingsProps) => {
	const { settings } = useSettings(entity)
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
