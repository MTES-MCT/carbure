import { useEffect } from "react"

import { EntitySelection } from "../../common/hooks/helpers/use-entity"

import * as api from "../api"
import useAPI from "../../common/hooks/helpers/use-api"
import { Settings } from "../../common/types"

export type SettingsGetter = {
  loading: boolean
  error: string | null
  data: Settings | null
  resolve: () => void
}

// fetches current snapshot when parameters change
export function useGetSettings(entity: EntitySelection): SettingsGetter {
  const [settings, resolveSettings] = useAPI(api.getSettings)

  function resolve() {
    return resolveSettings().cancel
  }

  useEffect(resolve, [resolveSettings, entity])

  return { ...settings, resolve }
}
