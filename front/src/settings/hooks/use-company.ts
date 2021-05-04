import { EntitySelection } from "carbure/hooks/use-entity"
import { SettingsGetter } from "./use-get-settings"

import * as api from "../api"
import useAPI from "common/hooks/use-api"

export function toggleMAC(toggle: boolean, entityID: number) {
  return toggle ? api.enableMAC(entityID) : api.disableMAC(entityID)
}

export function toggleTrading(toggle: boolean, entityID: number) {
  return toggle ? api.enableTrading(entityID) : api.disableTrading(entityID)
}

export interface CompanySettingsHook {
  isLoading: boolean
  hasMAC: boolean
  hasTrading: boolean
  onChangeMAC: (checked: boolean) => void
  onChangeTrading: (checked: boolean) => void
}

export default function useCompany(
  entity: EntitySelection,
  settings: SettingsGetter
): CompanySettingsHook {
  const hasMAC: boolean = entity?.has_mac ?? false
  const hasTrading: boolean = entity?.has_trading ?? false

  const [requestMAC, resolveToggleMAC] = useAPI(toggleMAC)
  const [requestTrading, resolveToggleTrading] = useAPI(toggleTrading)

  const isLoading =
    settings.loading || requestMAC.loading || requestTrading.loading

  function onChangeMAC(checked: boolean): void {
    if (entity !== null) {
      resolveToggleMAC(checked, entity.id).then(settings.resolve)
    }
  }

  function onChangeTrading(checked: boolean): void {
    if (entity !== null) {
      resolveToggleTrading(checked, entity.id).then(settings.resolve)
    }
  }

  return {
    isLoading,
    hasMAC,
    hasTrading,
    onChangeMAC,
    onChangeTrading,
  }
}
