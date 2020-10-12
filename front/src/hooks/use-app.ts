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

export default function useApp() {
  const settings = useGetSettings()

  function getDefaultEntity() {
    return settings.data?.rights[0].entity.id
  }

  return { settings, getDefaultEntity }
}
