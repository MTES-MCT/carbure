import React from "react"
import { EntitySelection } from "../hooks/helpers/use-entity"
import { UserRight } from "../services/types"

import styles from "./settings.module.css"
import useApi, { ApiState }  from "../hooks/helpers/use-api"
import { enableMAC, disableMAC } from "../services/settings"

import { Box } from "./system"
import { SettingsGetter } from "../hooks/settings/use-get-settings"

type GeneralSettingsProps = {
  entity: EntitySelection,
  settings: SettingsGetter,
}
  
export const GeneralSettings = ({
  entity,
  settings,
}: GeneralSettingsProps) => {
  const currentEntitySettings: UserRight | undefined = settings.data?.rights.find(element => element.entity.id === entity)
  const hasMAC : boolean = currentEntitySettings?.entity.has_mac?? false
  const hasTrading : boolean = currentEntitySettings?.entity.has_trading?? false
  const [macEnabled, resolveMacEnabled] = useApi(enableMAC)
  const [macDisabled, resolveMacDisabled] = useApi(disableMAC)

  function onChangeMac(event: React.ChangeEvent<HTMLInputElement>) : void {
    if (entity === null) {
      return
    }
    if (event.target.checked) {
      resolveMacEnabled(entity).then(settings.resolve)
    } else {
      resolveMacDisabled(entity).then(settings.resolve)
    }
  }

  if (currentEntitySettings === undefined) {
    return null
  }

  return (
    <Box>
      <fieldset>
        <h3>Mises à Consommation</h3>
        <input type="checkbox" checked={hasMAC} onChange={onChangeMac} name="hasMAC" />
        <label>Ma société effectue des Mises à Consommation</label>
        <h3>Trading</h3>
        <input type="checkbox" checked={hasTrading} name="hasTrading" />
        <label>Ma société a une activité de négoce</label>
      </fieldset>
    </Box>  
  )
} 
  
type ProductionSitesSettingsProps = {
  data: number
}
  
export const ProductionSitesSettings = ({
  data,
}: ProductionSitesSettingsProps) => (
  <Box>
    <p>Sites de Production</p>
  </Box>
)

  
type DeliverySitesSettingsProps = {
  data: number
}
  
export const DeliverySitesSettings = ({
  data,
}: DeliverySitesSettingsProps) => (
  <Box>
    <p>Dépôts</p>
  </Box>
)

  
  
