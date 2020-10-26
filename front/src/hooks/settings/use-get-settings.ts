import { useEffect } from "react"

import { EntitySelection } from "../helpers/use-entity"

import * as api from "../../services/settings"
import useAPI from "../helpers/use-api"

// fetches current snapshot when parameters change
export function useGetSettings(
  entity: EntitySelection,
) {
  const [settings, resolveSettings] = useAPI(api.getSettings)

  function resolve() {
    return resolveSettings().cancel
  }

  useEffect(resolve, [resolveSettings, entity])

  return { ...settings, resolve }
}
