import { useEffect } from "react"

import { EntitySelection } from "carbure/hooks/use-entity"
import { Certificate } from "common/types"

import { confirm, prompt } from "common/components/dialog"
import * as api from "../api"
import useAPI from "common/hooks/use-api"
import { CertificatePromptFactory } from "../components/certificates"
import { ProductionSiteSettingsHook } from "./use-production-sites"
import { useNotificationContext } from "common/components/notifications"
import { findREDCertCertificates } from "common/api"

const REDCertPrompt = CertificatePromptFactory("REDCERT", findREDCertCertificates)

export interface REDCertCertificateSettingsHook {
  isEmpty: boolean
  isLoading: boolean
  certificates: Certificate[]
  addREDCertCertificate: () => void
  deleteREDCertCertificate: (d: Certificate) => void
  updateREDCertCertificate: (d: Certificate) => void
}

export default function useREDCertCertificates(
  entity: EntitySelection,
  productionSites: ProductionSiteSettingsHook
): REDCertCertificateSettingsHook {
  const notifications = useNotificationContext()

  const [requestGetREDCert, resolveGetREDCert] = useAPI(api.getREDCertCertificates)
  const [requestAddREDCert, resolveAddREDCert] = useAPI(api.addREDCertCertificate)
  const [requestDelREDCert, resolveDelREDCert] = useAPI(api.deleteREDCertCertificate)
  const [requestUpdateREDCert, resolveUpdateREDCert] = useAPI(api.updateREDCertCertificate) // prettier-ignore

  const entityID = entity?.id
  const certificates = requestGetREDCert.data ?? []

  const isLoading =
    requestGetREDCert.loading ||
    requestAddREDCert.loading ||
    requestDelREDCert.loading ||
    requestUpdateREDCert.loading

  const isEmpty = certificates.length === 0

  function refresh() {
    if (typeof entityID !== "undefined") {
      resolveGetREDCert(entityID)
      productionSites.refresh && productionSites.refresh()
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

  async function addREDCertCertificate() {
    const data = await prompt(
      "Ajout certificat REDCert",
      "Vous pouvez rechercher parmi les certificats recensés sur Carbure et ajouter celui qui vous correspond.",
      REDCertPrompt
    )

    if (typeof entityID !== "undefined" && data) {
      notifyCertificate(resolveAddREDCert(entityID, data.certificate_id), "ajouté")
    }
  }

  async function deleteREDCertCertificate(redcert: Certificate) {
    if (
      typeof entityID !== "undefined" &&
      (await confirm(
        "Suppression certificat",
        `Voulez-vous vraiment supprimer le certificat REDCert "${redcert.certificate_id}" ?`
      ))
    ) {
      notifyCertificate(
        resolveDelREDCert(entityID, redcert.certificate_id),
        "supprimé"
      )
    }
  }

  async function updateREDCertCertificate(iscc: Certificate) {
    const data = await prompt(
      "Mise à jour certificat REDCert",
      "Veuillez sélectionner un nouveau certificat pour remplacer l'ancien.",
      REDCertPrompt
    )

    if (typeof entityID !== "undefined" && data) {
      notifyCertificate(
        resolveUpdateREDCert(entityID, iscc.certificate_id, data.certificate_id),
        "mis à jour"
      )
    }
  }

  useEffect(() => {
    if (typeof entityID !== "undefined") {
      resolveGetREDCert(entityID)
    }
  }, [entityID, resolveGetREDCert])

  return {
    isLoading,
    isEmpty,
    certificates,
    addREDCertCertificate,
    deleteREDCertCertificate,
    updateREDCertCertificate,
  }
}
