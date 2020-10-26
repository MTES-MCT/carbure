import { useEffect } from "react"

import { Entity, Settings } from "../services/types"

import useAPI, { ApiState } from "./helpers/use-api"
import { getSettings } from "../services/settings"

function useGetSettings(): ApiState<Settings> {
  const [settings, resolve] = useAPI(getSettings)

  useEffect(() => {
    return resolve().cancel
  }, [resolve])

  return settings
}

export type AppHook = {
  settings: ApiState<Settings>
  hasEntity: (e: number) => boolean
  getEntity: (id: number) => Entity | null
  getDefaultEntity: () => number | undefined
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

  function getDefaultEntity() {
    return settings.data?.rights[0].entity.id
  }

  return { settings, hasEntity, getEntity, getDefaultEntity }
}
