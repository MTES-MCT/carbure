import { useEffect } from "react"

import { EntitySelection } from "carbure/hooks/use-entity"
import { DeliverySite, OwnershipType } from "common/types"

import useAPI from "common/hooks/use-api"
import * as api from "../api"
import { confirm, prompt } from "common/components/dialog"
import {
  DeliverySitePromptFactory,
  DeliverySiteFinderPromptFactory,
} from "../components/delivery-site"
import { useNotificationContext } from "common/components/notifications"

export interface EntityDeliverySite {
  depot: DeliverySite | null
  ownership_type: OwnershipType
  blending_is_outsourced: boolean
  blender: EntitySelection
}

export interface DeliverySiteSettingsHook {
  isEmpty: boolean
  isLoading: boolean
  deliverySites: EntityDeliverySite[]
  showDeliverySite: (d: EntityDeliverySite) => void
  addDeliverySite?: () => void
  deleteDeliverySite?: (d: EntityDeliverySite) => void
}

export default function useDeliverySites(
  entity: EntitySelection
): DeliverySiteSettingsHook {
  const notifications = useNotificationContext()

  const [requestGetDeliverySites, resolveGetDeliverySites] = useAPI(api.getDeliverySites); // prettier-ignore
  const [requestAddDeliverySite, resolveAddDeliverySite] = useAPI(api.addDeliverySite); // prettier-ignore
  const [requestDeleteDeliverySite, resolveDeleteDeliverySite] = useAPI(api.deleteDeliverySite); // prettier-ignore

  const entityID = entity?.id
  const deliverySites = requestGetDeliverySites.data ?? []

  const isEmpty = deliverySites.length === 0
  const isLoading =
    requestGetDeliverySites.loading ||
    requestAddDeliverySite.loading ||
    requestDeleteDeliverySite.loading

  function refresh() {
    if (typeof entityID !== "undefined") {
      resolveGetDeliverySites(entityID)
    }
  }

  async function addDeliverySite() {
    const data = await prompt(
      "Ajouter dépôt",
      "Veuillez rechercher un dépôt que vous utilisez.",
      DeliverySiteFinderPromptFactory(entity)
    )

    if (typeof entityID !== "undefined" && data && data.depot) {
      const res = await resolveAddDeliverySite(
        entityID,
        data.depot.depot_id,
        data.ownership_type,
        data.blending_is_outsourced,
        data.blender
      )

      if (res) {
        refresh()

        notifications.push({
          level: "success",
          text: "Le dépôt a bien été ajouté !",
        })
      } else {
        notifications.push({
          level: "error",
          text: "Impossible d'ajouter le dépôt.",
        })
      }
    }
  }

  async function showDeliverySite(ds: EntityDeliverySite) {
    prompt(
      "Détails du dépôt",
      `Informations concernant le dépôt ${ds.depot!.name} (non modifiable)`,
      DeliverySitePromptFactory(ds)
    )
  }

  async function deleteDeliverySite(ds: EntityDeliverySite) {
    const shouldDelete = await confirm(
      "Supprimer dépôt",
      `Voulez-vous supprimer le dépôt "${ds.depot!.name}" de votre liste ?`
    )

    if (typeof entityID !== "undefined" && shouldDelete) {
      const res = await resolveDeleteDeliverySite(entityID, ds.depot!.depot_id)

      if (res) {
        refresh()

        notifications.push({
          level: "success",
          text: "Le dépôt a bien été supprimé !",
        })
      } else {
        notifications.push({
          level: "error",
          text: "Impossible de supprimer le dépôt.",
        })
      }
    }
  }

  useEffect(() => {
    if (typeof entityID !== "undefined") {
      resolveGetDeliverySites(entityID)
    }
  }, [entityID, resolveGetDeliverySites])

  return {
    isLoading,
    isEmpty,
    deliverySites,
    addDeliverySite,
    showDeliverySite,
    deleteDeliverySite,
  }
}
