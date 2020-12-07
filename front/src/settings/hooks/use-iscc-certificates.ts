import { useEffect } from "react"

import { EntitySelection } from "../../common/hooks/helpers/use-entity"
import { ISCCCertificate } from "../../common/types"

import { confirm, prompt } from "../../common/system/dialog"
import * as api from "../api"
import useAPI from "../../common/hooks/helpers/use-api"
import { ISCCPrompt } from "../components/iscc-certificates-settings"
import { ProductionSiteSettingsHook } from "./use-production-sites"
import { useNotificationContext } from "../../common/system/notifications"

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
  const notifications = useNotificationContext()

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
      productionSites.refresh()
    }
  }

  async function notifyCertificate(promise: Promise<any>, action: string) {
    const res = await promise

    if (res) {
      refresh()

      notifications.push({
        level: "success",
        text: `Le certificat a bien été ${action} !`,
      })
    } else {
      notifications.push({
        level: "error",
        text: `Le certificat n'a pas pu être ${action}.`,
      })
    }
  }

  async function addISCCCertificate() {
    const data = await prompt(
      "Ajout certificat ISCC",
      "Vous pouvez rechercher parmi les certificats recensés sur Carbure et ajouter celui qui vous correspond.",
      ISCCPrompt
    )

    if (entityID && data) {
      notifyCertificate(resolveAddISCC(entityID, data.certificate_id), "ajouté")
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
      notifyCertificate(
        resolveDelISCC(entityID, iscc.certificate_id),
        "supprimé"
      )
    }
  }

  async function updateISCCCertificate(iscc: ISCCCertificate) {
    const data = await prompt(
      "Mise à jour certificat ISCC",
      "Veuillez sélectionner un nouveau certificat pour remplacer l'ancien.",
      ISCCPrompt
    )

    if (entityID && data) {
      notifyCertificate(
        resolveUpdateISCC(entityID, iscc.certificate_id, data.certificate_id),
        "mis à jour"
      )
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
