import { Entity } from "common/types"
import { useGetSettings, SettingsGetter } from "settings/hooks/use-get-settings"

export type AppHook = {
  settings: SettingsGetter
  hasEntity: (e: number) => boolean
  hasEntities: () => boolean
  getEntity: (id: number) => Entity | null
  getDefaultEntity: () => string
}

export function useApp(): AppHook {
  const settings = useGetSettings()

  function getEntity(entity: number) {
    const rights = settings.data?.rights
    return rights?.find((r) => r.entity.id === entity)?.entity ?? null
  }

  function hasEntity(entity: number) {
    return Boolean(getEntity(entity))
  }

  function hasEntities() {
    return Boolean(settings.data?.rights.length)
  }

  function getDefaultEntity() {
    if (!settings.data || settings.data.rights.length === 0) {
      return "pending"
    } else {
      return `${settings.data.rights[0].entity.id}`
    }
  }

  return { settings, hasEntity, hasEntities, getEntity, getDefaultEntity }
}
