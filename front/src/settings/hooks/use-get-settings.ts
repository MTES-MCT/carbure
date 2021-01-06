import { useEffect } from "react"

import * as api from "../api"
import useAPI from "common/hooks/use-api"
import { Settings } from "common/types"

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
    resolveSettings()
  }

  useEffect(resolve, [resolveSettings])

  return { ...settings, resolve }
}
