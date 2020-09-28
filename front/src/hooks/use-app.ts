import { useEffect, useState } from "react"

import { Entity, Settings } from "../services/types"

import useAPI, { ApiState } from "./use-api"
import { getSettings } from "../services/settings"

export type EntitySelection = {
  selected: Entity | null
  selectEntity: (e: EntitySelection["selected"]) => void
}

function useEntity(): EntitySelection {
  const [selected, selectEntity] = useState<Entity | null>(null)
  return { selected, selectEntity }
}

function useGetSettings(): ApiState<Settings> {
  const [settings, resolve] = useAPI<Settings>()

  useEffect(() => {
    resolve(getSettings())
  }, [resolve])

  return settings
}

export default function useApp() {
  const entity = useEntity()
  const settings = useGetSettings()

  // select the default entity if not already done
  if (entity.selected === null && settings.data) {
    entity.selectEntity(settings.data.rights[0].entity)
  }

  return { entity, settings }
}
