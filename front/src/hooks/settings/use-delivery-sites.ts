import { useEffect, useState } from "react"

import { EntitySelection } from "../helpers/use-entity"
import { DeliverySite } from "../../services/types"

import useAPI from "../helpers/use-api"
import * as common from "../../services/common"
import { prompt } from "../../components/system/dialog"
import { DeliverySitePromptFactory } from "../../components/settings/delivery-site-settings"

export interface DeliverySiteSettingsHook {
  isEmpty: boolean
  isLoading: boolean
  query: string
  deliverySites: DeliverySite[]
  createDeliverySite: () => void
  showDeliverySite: (d: DeliverySite) => void
  setQuery: (q: string) => void
}

export default function useDeliverySites(
  entity: EntitySelection
): DeliverySiteSettingsHook {
  const [query, setQuery] = useState("")
  const [requestGetDeliverySites, resolveGetDeliverySites] = useAPI(common.findDeliverySites); // prettier-ignore
  const [requestAddDeliverySite, resolveAddDeliverySite] = useAPI(common.addDeliverySite); // prettier-ignore

  const entityID = entity?.id
  const deliverySites = requestGetDeliverySites.data ?? []

  const isLoading = requestGetDeliverySites.loading || requestAddDeliverySite.loading // prettier-ignore
  const isEmpty = deliverySites.length === 0 || query.length === 0

  async function createDeliverySite() {
    const data = await prompt(
      "Ajouter un dépôt",
      "Veuillez entrer les informations de votre nouveau dépôt.",
      DeliverySitePromptFactory()
    )

    if (entityID && data && data.country) {
      resolveAddDeliverySite(
        data.name,
        data.city,
        data.country.code_pays,
        data.depot_id,
        data.depot_type,
        data.address,
        data.postal_code,
        data.ownership_type
      ).then(() => setQuery(data.depot_id))
    }
  }

  async function showDeliverySite(ds: DeliverySite) {
    prompt(
      "Détails du dépôt",
      `Informations concernant le dépôt ${ds.depot_id}`,
      DeliverySitePromptFactory(ds, true)
    )
  }

  useEffect(() => {
    if (query) {
      resolveGetDeliverySites(query)
    }
  }, [query, resolveGetDeliverySites])

  return {
    isLoading,
    isEmpty,
    query,
    deliverySites,
    createDeliverySite,
    showDeliverySite,
    setQuery,
  }
}
