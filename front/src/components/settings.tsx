import React from "react"
import { EntitySelection } from "../hooks/helpers/use-entity"
import { SettingsGetter } from "../hooks/use-app"

import styles from "./settings.module.css"
import useApi from "../hooks/helpers/use-api"
import { enableMAC, disableMAC } from "../services/settings"

import { Box } from "./system"

type GeneralSettingsProps = {
  entity: EntitySelection
  settings: SettingsGetter
}

export const GeneralSettings = ({ entity, settings }: GeneralSettingsProps) => {
  const hasMAC: boolean = entity?.has_mac ?? false
  const hasTrading: boolean = entity?.has_trading ?? false
  const [macEnabled, resolveMacEnabled] = useApi(enableMAC)
  const [macDisabled, resolveMacDisabled] = useApi(disableMAC)

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
    <Box>
      <fieldset>
        <h3>Mises à Consommation</h3>
        <input
          type="checkbox"
          defaultChecked={hasMAC}
          onChange={onChangeMac}
          name="hasMAC"
        />
        <label>Ma société effectue des Mises à Consommation</label>
        <h3>Trading</h3>
        <input type="checkbox" defaultChecked={hasTrading} name="hasTrading" />
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

export const DeliverySitesSettings = ({ data }: DeliverySitesSettingsProps) => (
  <Box>
    <p>Dépôts</p>
  </Box>
)
