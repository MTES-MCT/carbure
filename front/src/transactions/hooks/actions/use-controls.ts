import { EntitySelection } from "carbure/hooks/use-entity"

import * as api from "transactions/api"
import useAPI from "../../../common/hooks/use-api"

import { confirm } from "../../../common/components/dialog"
import { useNotificationContext } from "../../../common/components/notifications"
import { EntityType } from "common/types"

function hidePoster(entity: EntitySelection) {
  switch (entity?.entity_type) {
    case EntityType.Administration:
      return api.hideAdminLots
    case EntityType.Auditor:
      return api.hideAuditorLots
    default:
      return async () => {}
  }
}

function highlightPoster(entity: EntitySelection) {
  switch (entity?.entity_type) {
    case EntityType.Administration:
      return api.hideAdminLots
    case EntityType.Auditor:
      return api.hideAuditorLots
    default:
      return async () => {}
  }
}

export interface LotController {
  loading: boolean
  hideLot: (i: number) => Promise<boolean>
  highlightLot: (i: number) => Promise<boolean>
}

export default function useControlLots(
  entity: EntitySelection,
  refresh: () => void
): LotController {
  const notifications = useNotificationContext()
  const [hideReq, resolveHideLot] = useAPI(hidePoster(entity))
  const [highlightReq, resolveHighlightLot] = useAPI(highlightPoster(entity))

  async function hideLot(txID: number) {
    const shouldHide = await confirm(
      "Cacher le lot",
      "Voulez-vous ne plus voir ce lot dans la liste ?"
    )

    if (entity !== null && shouldHide) {
      const res = await resolveHideLot(entity.id, [txID])

      if (res) {
        refresh()

        notifications.push({
          level: "success",
          text: "Le lot a bien été caché !",
        })
      }
    }

    return shouldHide
  }

  async function highlightLot(txID: number) {
    const shouldHighlight = await confirm(
      "Marquer ce lot",
      "Voulez-vous mettre ce lot de côté pour l'étudier plus tard ?"
    )

    if (entity !== null && shouldHighlight) {
      const res = await resolveHighlightLot(entity.id, [txID])

      if (res) {
        refresh()

        notifications.push({
          level: "success",
          text: "Le lot a bien été marqué !",
        })
      }
    }

    return shouldHighlight
  }

  return {
    loading: hideReq.loading && highlightReq.loading,
    hideLot,
    highlightLot,
  }
}
