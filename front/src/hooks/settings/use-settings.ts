import { EntitySelection } from "../helpers/use-entity"
import { useGetSettings } from "./use-get-settings"

export default function useSettings(entity: EntitySelection) {
  const settings = useGetSettings(entity)

  return {
    entity,
    settings,
  }
}
