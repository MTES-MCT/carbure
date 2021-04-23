import { useEffect } from "react"

import { EntitySelection } from "carbure/hooks/use-entity"
import { Certificate } from "common/types"

import { confirm, prompt } from "common/components/dialog"
import * as api from "../api"
import useAPI from "common/hooks/use-api"
import { CertificatePrompt } from "../components/certificates"
import { ProductionSiteSettingsHook } from "./use-production-sites"
import { useNotificationContext } from "common/components/notifications"
import { findSNCertificates } from "common/api"

export interface SNCertificateSettingsHook {
  isEmpty: boolean
  isLoading: boolean
  certificates: Certificate[]
  addSNCertificate: () => void
  deleteSNCertificate: (d: Certificate) => void
  updateSNCertificate: (d: Certificate) => void
}

export default function useSNCertificates(
  entity: EntitySelection,
  productionSites: ProductionSiteSettingsHook
): SNCertificateSettingsHook {
  const notifications = useNotificationContext()

  const [requestGetSN, resolveGetSN] = useAPI(
    api.getSNCertificates
  )
  const [requestAddSN, resolveAddSN] = useAPI(
    api.addSNCertificate
  )
  const [requestDelSN, resolveDelSN] = useAPI(
    api.deleteSNCertificate
  )
  const [requestUpdateSN, resolveUpdateSN] = useAPI(api.updateSNCertificate) // prettier-ignore

  const entityID = entity?.id
  const certificates = requestGetSN.data ?? []

  const isLoading =
    requestGetSN.loading ||
    requestAddSN.loading ||
    requestDelSN.loading ||
    requestUpdateSN.loading

  const isEmpty = certificates.length === 0

  function refresh() {
    if (typeof entityID !== "undefined") {
      resolveGetSN(entityID)
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

  async function addSNCertificate() {
    const data = await prompt<Certificate>((resolve) => (
      <CertificatePrompt
        type="SN"
        title="Ajout certificat Système National"
        description="Vous pouvez rechercher parmi les certificats recensés sur Carbure et ajouter celui qui vous correspond."
        findCertificates={findSNCertificates}
        onResolve={resolve}
      />
    ))

    if (typeof entityID !== "undefined" && data) {
      notifyCertificate(
        resolveAddSN(entityID, data.certificate_id),
        "ajouté"
      )
    }
  }

  async function deleteSNCertificate(sn: Certificate) {
    if (
      typeof entityID !== "undefined" &&
      (await confirm(
        "Suppression certificat",
        `Voulez-vous vraiment supprimer le certificat Système National "${sn.certificate_id}" ?`
      ))
    ) {
      notifyCertificate(
        resolveDelSN(entityID, sn.certificate_id),
        "supprimé"
      )
    }
  }

  async function updateSNCertificate(sn: Certificate) {
    const data = await prompt<Certificate>((resolve) => (
      <CertificatePrompt
        type="SN"
        title="Mise à jour certificat Système National"
        description="Veuillez sélectionner un nouveau certificat pour remplacer l'ancien."
        findCertificates={findSNCertificates}
        onResolve={resolve}
      />
    ))

    if (typeof entityID !== "undefined" && data) {
      notifyCertificate(
        resolveUpdateSN(
          entityID,
          sn.certificate_id,
          data.certificate_id
        ),
        "mis à jour"
      )
    }
  }

  useEffect(() => {
    if (typeof entityID !== "undefined") {
      resolveGetSN(entityID)
    }
  }, [entityID, resolveGetSN])

  return {
    isLoading,
    isEmpty,
    certificates,
    addSNCertificate,
    deleteSNCertificate,
    updateSNCertificate,
  }
}
