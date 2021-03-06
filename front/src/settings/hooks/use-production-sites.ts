import { useEffect } from "react"

import { EntitySelection } from "carbure/hooks/use-entity"
import { ProductionSiteDetails } from "common/types"

import useAPI from "common/hooks/use-api"
import * as api from "../api"
import {
  ProductionSitePromptFactory,
  ProductionSiteState,
} from "../components/production-site"
import { confirm, prompt } from "common/components/dialog"
import { useNotificationContext } from "common/components/notifications"

export interface ProductionSiteSettingsHook {
  isEmpty: boolean
  isLoading: boolean
  productionSites: ProductionSiteDetails[]
  editProductionSite: (p: ProductionSiteDetails) => void
  createProductionSite?: () => void
  removeProductionSite?: (p: ProductionSiteDetails) => void
  refresh?: () => void
}

export default function useProductionSites(
  entity: EntitySelection
): ProductionSiteSettingsHook {
  const notifications = useNotificationContext()

  const [requestGetProductionSites, resolveGetProductionSites] = useAPI(api.getProductionSites) // prettier-ignore
  const [requestAddProductionSite, resolveAddProductionSite] = useAPI(api.addProductionSite) // prettier-ignore
  const [requestDelProductionSite, resolveDelProductionSite] = useAPI(api.deleteProductionSite) // prettier-ignore
  const [requestUpdateProductionSite, resolveUpdateProductionSite] = useAPI(api.updateProductionSite) // prettier-ignore

  const [requestSetProductionSiteMP, resolveSetProductionSiteMP] = useAPI(api.setProductionSiteMP) // prettier-ignore
  const [requestSetProductionSiteBC, resolveSetProductionSiteBC] = useAPI(api.setProductionSiteBC) // prettier-ignore
  const [requestSetProductionSiteCertificates, resolveSetProductionSiteCertificates] = useAPI(api.setProductionSiteCertificates) // prettier-ignore

  const entityID = entity?.id
  const productionSites = requestGetProductionSites.data ?? []

  const isLoading =
    requestAddProductionSite.loading ||
    requestGetProductionSites.loading ||
    requestDelProductionSite.loading ||
    requestSetProductionSiteBC.loading ||
    requestSetProductionSiteMP.loading ||
    requestUpdateProductionSite.loading ||
    requestSetProductionSiteCertificates.loading

  const isEmpty = productionSites.length === 0

  function refresh() {
    if (typeof entityID !== "undefined") {
      resolveGetProductionSites(entityID)
    }
  }

  async function createProductionSite() {
    const data = await prompt(
      "Ajout site de production",
      "Veuillez entrer les informations de votre nouveau site de production.",
      ProductionSitePromptFactory(entity)
    )

    if (typeof entityID !== "undefined" && data && data.country) {
      const ps = await resolveAddProductionSite(
        entityID,
        data.name,
        data.date_mise_en_service,
        data.country.code_pays,
        data.ges_option,
        data.site_id,
        data.city,
        data.postal_code,
        data.eligible_dc,
        data.dc_reference,
        data.manager_name,
        data.manager_phone,
        data.manager_email
      )

      if (ps) {
        const mps = data.matieres_premieres.map((mp) => mp.code)
        await resolveSetProductionSiteMP(ps.id, mps)

        const bcs = data.biocarburants.map((bc) => bc.code)
        await resolveSetProductionSiteBC(ps.id, bcs)

        const cs = data.certificates.map((c) => c.certificate_id)
        await resolveSetProductionSiteCertificates(entityID, ps.id, cs)

        notifications.push({
          level: "success",
          text: "Le site de production a bien été créé !",
        })

        refresh()
      } else {
        notifications.push({
          level: "error",
          text: "Impossible de créer le site de production.",
        })
      }
    }
  }

  async function editProductionSite(ps: ProductionSiteDetails) {
    const data = await prompt<ProductionSiteState>(
      "Modification site de production",
      "Veuillez entrer les nouvelles informations de votre site de production.",
      ProductionSitePromptFactory(entity, ps)
    )

    if (typeof entityID !== "undefined" && data && data.country) {
      const res = await resolveUpdateProductionSite(
        entityID,
        ps.id,
        data.name,
        data.date_mise_en_service,
        data.country.code_pays,
        data.ges_option,
        data.site_id,
        data.city,
        data.postal_code,
        data.eligible_dc,
        data.dc_reference,
        data.manager_name,
        data.manager_phone,
        data.manager_email
      )

      const mps = data.matieres_premieres.map((mp) => mp.code)
      await resolveSetProductionSiteMP(ps.id, mps)

      const bcs = data.biocarburants.map((bc) => bc.code)
      await resolveSetProductionSiteBC(ps.id, bcs)

      const cs = data.certificates.map((c) => c.certificate_id)
      await resolveSetProductionSiteCertificates(entityID, ps.id, cs)

      if (res) {
        refresh()

        notifications.push({
          level: "success",
          text: "Le site de production a bien été modifié !",
        })
      } else {
        notifications.push({
          level: "error",
          text: "Impossible de modifier le site de production.",
        })
      }
    }
  }

  async function removeProductionSite(ps: ProductionSiteDetails) {
    if (
      await confirm(
        "Suppression site",
        `Voulez-vous vraiment supprimer le site de production "${ps.name}" ?`
      )
    ) {
      const res = resolveDelProductionSite(ps.id)

      if (res) {
        refresh()

        notifications.push({
          level: "success",
          text: "Le site de production a bien été supprimé !",
        })
      } else {
        notifications.push({
          level: "error",
          text: "Impossible de supprimer le site de production",
        })
      }
    }
  }

  useEffect(() => {
    if (typeof entityID !== "undefined") {
      resolveGetProductionSites(entityID)
    }
  }, [entityID, resolveGetProductionSites])

  return {
    isEmpty,
    isLoading,
    productionSites,
    createProductionSite,
    editProductionSite,
    removeProductionSite,
    refresh,
  }
}
