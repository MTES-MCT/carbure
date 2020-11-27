import { useEffect } from "react"

import { Entity, Settings } from "../services/types"

import useAPI from "./helpers/use-api"
import * as api from "../services/settings"

export type SettingsGetter = {
  loading: boolean
  error: string | null
  data: Settings | null
  resolve: () => void
}

// fetches current snapshot when parameters change
export function useGetSettings(): SettingsGetter {
  const [settings, resolveSettings] = useAPI(api.getSettings)

  function resolve() {
    return resolveSettings().cancel
  }

  useEffect(resolve, [resolveSettings])

  return { ...settings, resolve }
}

export type AppHook = {
  settings: SettingsGetter
  hasEntity: (e: number) => boolean
  hasEntities: () => boolean
  getEntity: (id: number) => Entity | null
  getDefaultEntity: () => string
}

export default function useApp(): AppHook {
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
