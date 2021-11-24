import { useEffect } from "react"
import { useTranslation } from "react-i18next"

import { Entity } from "carbure/types"
import { DeliverySite, OwnershipType } from "common/types"

import useAPI from "common/hooks/use-api"
import * as api from "../api"
import { confirm, prompt } from "common/components/dialog"
import {
  DeliverySitePrompt,
  DeliverySiteFinderPrompt,
} from "../components/delivery-site"
import { useNotificationContext } from "common/components/notifications"

export interface EntityDeliverySite {
  depot: DeliverySite | null
  ownership_type: OwnershipType
  blending_is_outsourced: boolean
  blender: Entity | null
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
  entity: Entity
): DeliverySiteSettingsHook {
  const { t } = useTranslation()
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
    const data = await prompt<EntityDeliverySite>((resolve) => (
      <DeliverySiteFinderPrompt entity={entity} onResolve={resolve} />
    ))

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
          text: t("Le dépôt a bien été ajouté !"),
        })
      } else {
        notifications.push({
          level: "error",
          text: t("Impossible d'ajouter le dépôt."),
        })
      }
    }
  }

  async function showDeliverySite(ds: EntityDeliverySite) {
    prompt((resolve) => (
      <DeliverySitePrompt
        title={t("Ajouter dépôt")}
        description={t("Veuillez rechercher un dépôt que vous utilisez.")}
        deliverySite={ds}
        onResolve={resolve}
      />
    ))
  }

  async function deleteDeliverySite(ds: EntityDeliverySite) {
    const shouldDelete = await confirm(
      t("Supprimer dépôt"),
      t("Voulez-vous supprimer le dépôt {{depot}} de votre liste ?", { depot: ds.depot!.name }) // prettier-ignore
    )

    if (typeof entityID !== "undefined" && shouldDelete) {
      const res = await resolveDeleteDeliverySite(entityID, ds.depot!.depot_id)

      if (res) {
        refresh()

        notifications.push({
          level: "success",
          text: t("Le dépôt a bien été supprimé !"),
        })
      } else {
        notifications.push({
          level: "error",
          text: t("Impossible de supprimer le dépôt."),
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
