import { UserRight } from "common/types"
import { useGetSettings, SettingsGetter } from "settings/hooks/use-get-settings"

export type AppHook = {
  settings: SettingsGetter
  hasEntity: (e: number) => boolean
  hasEntities: () => boolean
  getRights: (id: number) => UserRight | null
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

  return { settings, hasEntity, hasEntities, getRights }
}
