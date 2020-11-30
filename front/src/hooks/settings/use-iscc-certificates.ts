import { useEffect } from "react"

import { EntitySelection } from "../helpers/use-entity"
import { ISCCCertificate } from "../../services/types"

import { confirm, prompt } from "../../components/system/dialog"
import * as api from "../../services/settings"
import useAPI from "../helpers/use-api"
import { ISCCPrompt } from "../../components/settings/iscc-certificates-settings"
import { ProductionSiteSettingsHook } from "./use-production-sites"

export interface ISCCCertificateSettingsHook {
  isEmpty: boolean
  isLoading: boolean
  certificates: ISCCCertificate[]
  addISCCCertificate: () => void
  deleteISCCCertificate: (d: ISCCCertificate) => void
  updateISCCCertificate: (d: ISCCCertificate) => void
}

export default function useISCCCertificates(
  entity: EntitySelection,
  productionSites: ProductionSiteSettingsHook
): ISCCCertificateSettingsHook {
  const [requestGetISCC, resolveGetISCC] = useAPI(api.getISCCCertificates)
  const [requestAddISCC, resolveAddISCC] = useAPI(api.addISCCCertificate)
  const [requestDelISCC, resolveDelISCC] = useAPI(api.deleteISCCCertificate)
  const [requestUpdateISCC, resolveUpdateISCC] = useAPI(api.updateISCCCertificate) // prettier-ignore

  const entityID = entity?.id
  const certificates = requestGetISCC.data ?? []

  const isLoading =
    requestGetISCC.loading ||
    requestAddISCC.loading ||
    requestDelISCC.loading ||
    requestUpdateISCC.loading

  const isEmpty = certificates.length === 0

  function refresh() {
    if (entityID) {
      resolveGetISCC(entityID)
    }
  }

  async function addISCCCertificate() {
    const data = await prompt(
      "Ajout certificat ISCC",
      "Vous pouvez rechercher parmi les certificats recensés sur Carbure et ajouter celui qui vous correspond.",
      ISCCPrompt
    )

    if (entityID && data) {
      resolveAddISCC(entityID, data.certificate_id).then(() =>
        resolveGetISCC(entityID)
      )
    }
  }

  async function deleteISCCCertificate(iscc: ISCCCertificate) {
    if (
      entityID &&
      (await confirm(
        "Suppression certificat",
        `Voulez-vous vraiment supprimer le certificat ISCC "${iscc.certificate_id}" ?`
      ))
    ) {
      resolveDelISCC(entityID, iscc.certificate_id).then(() => {
        refresh()
        productionSites.refresh()
      })
    }
  }

  async function updateISCCCertificate(iscc: ISCCCertificate) {
    const data = await prompt(
      "Mise à jour certificat ISCC",
      "Veuillez sélectionner un nouveau certificat pour remplacer l'ancien.",
      ISCCPrompt
    )

    if (entityID && data) {
      resolveUpdateISCC(
        entityID,
        iscc.certificate_id,
        data.certificate_id
      ).then(() => {
        refresh()
        productionSites.refresh()
      })
    }
  }

  useEffect(() => {
    if (entityID) {
      resolveGetISCC(entityID)
    }
  }, [entityID, resolveGetISCC])

  return {
    isLoading,
    isEmpty,
    certificates,
    addISCCCertificate,
    deleteISCCCertificate,
    updateISCCCertificate,
  }
}
