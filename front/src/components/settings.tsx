import React from "react"
import { EntitySelection } from "../hooks/helpers/use-entity"
import { UserRight } from "../services/types"

import styles from "./settings.module.css"
import { ApiState } from "../hooks/helpers/use-api"
import { Settings } from "../services/types"

import { Box } from "./system"

type GeneralSettingsProps = {
  entity: EntitySelection,
  settings: ApiState<Settings>,
}
  
export const GeneralSettings = ({
  entity,
  settings,
}: GeneralSettingsProps) => {
  const currentEntitySettings: UserRight | undefined = settings.data?.rights.find(element => element.entity.id === entity)

  if (currentEntitySettings === undefined) {
    return null
  }

  return (
    <Box>
      <fieldset>
        <h3>Mises à Consommation</h3>
        <input type="checkbox" checked={currentEntitySettings.entity.has_mac} name="checkbox" id="checkbox-mac" />
        <label>Ma société effectue des Mises à Consommation</label>
        <h3>Trading</h3>
        <input type="checkbox" checked={currentEntitySettings.entity.has_trading} name="checkbox" id="checkbox-trading" />
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

  
  
