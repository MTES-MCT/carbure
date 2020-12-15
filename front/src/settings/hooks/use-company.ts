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
  onChangeMAC: (e: React.ChangeEvent<HTMLInputElement>) => void
  onChangeTrading: (e: React.ChangeEvent<HTMLInputElement>) => void
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

  function onChangeMAC(e: React.ChangeEvent<HTMLInputElement>): void {
    if (entity !== null) {
      resolveToggleMAC(e.target.checked, entity.id).then(settings.resolve)
    }
  }

  function onChangeTrading(e: React.ChangeEvent<HTMLInputElement>): void {
    if (entity !== null) {
      resolveToggleTrading(e.target.checked, entity.id).then(settings.resolve)
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
