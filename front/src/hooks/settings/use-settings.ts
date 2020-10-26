import { EntitySelection } from "../helpers/use-entity"
import { SettingsGetter } from "../use-app"

export default function useSettings(
  entity: EntitySelection,
  settings: SettingsGetter
) {
  return {
    entity,
    settings,
  }
}
