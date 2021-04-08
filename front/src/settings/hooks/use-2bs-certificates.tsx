import { useEffect } from "react"
import { CertificatePrompt } from "../components/certificates"
import { confirm, prompt } from "common/components/dialog"
import { useNotificationContext } from "common/components/notifications"
import * as api from "../api"
import { Certificate } from "common/types"
import useAPI from "common/hooks/use-api"
import { EntitySelection } from "carbure/hooks/use-entity"
import { ProductionSiteSettingsHook } from "./use-production-sites"
import { find2BSCertificates } from "common/api"

export interface DBSCertificateSettingsHook {
  isEmpty: boolean
  isLoading: boolean
  certificates: Certificate[]
  add2BSCertificate: () => void
  delete2BSCertificate: (d: Certificate) => void
  update2BSCertificate: (d: Certificate) => void
}

export default function use2BSCertificates(
  entity: EntitySelection,
  productionSites: ProductionSiteSettingsHook
): DBSCertificateSettingsHook {
  const notifications = useNotificationContext()

  const [requestGet2BS, resolveGet2BS] = useAPI(api.get2BSCertificates)
  const [requestAdd2BS, resolveAdd2BS] = useAPI(api.add2BSCertificate)
  const [requestDel2BS, resolveDel2BS] = useAPI(api.delete2BSCertificate)
  const [requestUpdate2BS, resolveUpdate2BS] = useAPI(api.update2BSCertificate)

  const entityID = entity?.id
  const certificates = requestGet2BS.data ?? []

  const isLoading =
    requestGet2BS.loading ||
    requestAdd2BS.loading ||
    requestDel2BS.loading ||
    requestUpdate2BS.loading

  const isEmpty = certificates.length === 0

  function refresh() {
    if (typeof entityID !== "undefined") {
      resolveGet2BS(entityID)
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

  async function add2BSCertificate() {
    const data = await prompt<Certificate>((resolve) => (
      <CertificatePrompt
        type="2BS"
        title="Ajout certificat 2BS"
        description="Vous pouvez rechercher parmi les certificats recensés sur Carbure et ajouter celui qui vous correspond."
        findCertificates={find2BSCertificates}
        onResolve={resolve}
      />
    ))

    if (typeof entityID !== "undefined" && data) {
      notifyCertificate(resolveAdd2BS(entityID, data.certificate_id), "ajouté")
    }
  }

  async function delete2BSCertificate(dbs: Certificate) {
    if (
      typeof entityID !== "undefined" &&
      (await confirm(
        "Suppression certificat",
        `Voulez-vous vraiment supprimer le certificat 2BS "${dbs.certificate_id}" ?`
      ))
    ) {
      notifyCertificate(resolveDel2BS(entityID, dbs.certificate_id), "supprimé")
    }
  }

  async function update2BSCertificate(dbs: Certificate) {
    const data = await prompt<Certificate>((resolve) => (
      <CertificatePrompt
        type="2BS"
        title="Mise à jour certificat 2BS"
        description="Veuillez sélectionner un nouveau certificat pour remplacer l'ancien."
        findCertificates={find2BSCertificates}
        onResolve={resolve}
      />
    ))

    if (typeof entityID !== "undefined" && data) {
      notifyCertificate(
        resolveUpdate2BS(entityID, dbs.certificate_id, data.certificate_id),
        "mis à jour"
      )
    }
  }

  useEffect(() => {
    if (typeof entityID !== "undefined") {
      resolveGet2BS(entityID)
    }
  }, [entityID, resolveGet2BS])

  return {
    isLoading,
    isEmpty,
    certificates,
    add2BSCertificate,
    delete2BSCertificate,
    update2BSCertificate,
  }
}
