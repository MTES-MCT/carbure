import { UserRight } from "common/types"
import { useGetSettings, SettingsGetter } from "settings/hooks/use-get-settings"
import { EntitySelection } from "./use-entity"

export type AppHook = {
  settings: SettingsGetter
  hasEntity: (e: number) => boolean
  hasEntities: () => boolean
  getRights: (id: number) => UserRight | null
  getFirstEntity: () => EntitySelection
  isAuthenticated: () => boolean
  isProduction: () => boolean
}

export function useApp(): AppHook {
  const settings = useGetSettings()

  function getRights(entity: number) {
    const rights = settings.data?.rights
    return rights?.find((r) => r.entity.id === entity) ?? null
  }

  function hasEntity(entity: number) {
    return Boolean(getRights(entity))
  }

  function hasEntities() {
    return Boolean(settings.data?.rights.length)
  }

  function getFirstEntity() {
    return settings.data?.rights[0]?.entity ?? null
  }

  function isAuthenticated() {
    return settings.error !== "User not verified"
  }

  function isProduction() {
    return window.location.hostname === "carbure.beta.gouv.fr"
  }

  return {
    settings,
    hasEntity,
    hasEntities,
    getRights,
    getFirstEntity,
    isAuthenticated,
    isProduction,
  }
}
