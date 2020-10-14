import { useEffect } from "react"

import { Settings } from "../services/types"

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
  getDefaultEntity: () => number | undefined
}

export default function useApp(): AppHook {
  const settings = useGetSettings()

  function hasEntity(entity: number) {
    return Boolean(settings.data?.rights.find((r) => r.entity.id === entity))
  }

  function getDefaultEntity() {
    return settings.data?.rights[0].entity.id
  }

  return { settings, hasEntity, getDefaultEntity }
}
