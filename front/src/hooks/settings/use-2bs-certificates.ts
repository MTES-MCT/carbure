import { useEffect } from "react"
import { DBSPrompt } from "../../components/settings/2bs-certificates-settings"
import { confirm, prompt } from "../../components/system/dialog"
import * as api from "../../services/settings"
import { DBSCertificate } from "../../services/types"
import useAPI from "../helpers/use-api"
import { EntitySelection } from "../helpers/use-entity"
import { ProductionSiteSettingsHook } from "./use-production-sites"

export interface DBSCertificateSettingsHook {
  isEmpty: boolean
  isLoading: boolean
  certificates: DBSCertificate[]
  add2BSCertificate: () => void
  delete2BSCertificate: (d: DBSCertificate) => void
  update2BSCertificate: (d: DBSCertificate) => void
}

export default function use2BSCertificates(
  entity: EntitySelection,
  productionSites: ProductionSiteSettingsHook
): DBSCertificateSettingsHook {
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
    if (entityID) {
      resolveGet2BS(entityID)
    }
  }

  async function add2BSCertificate() {
    const data = await prompt(
      "Ajout certificat 2BS",
      "Vous pouvez rechercher parmi les certificats recensés sur Carbure et ajouter celui qui vous correspond.",
      DBSPrompt
    )

    if (entityID && data) {
      resolveAdd2BS(entityID, data.certificate_id).then(refresh)
    }
  }

  async function delete2BSCertificate(dbs: DBSCertificate) {
    if (
      entityID &&
      (await confirm(
        "Suppresion certificat",
        `Voulez-vous vraiment supprimer le certificat 2BS "${dbs.certificate_id}" ?`
      ))
    ) {
      resolveDel2BS(entityID, dbs.certificate_id).then(() => {
        refresh()
        productionSites.refresh()
      })
    }
  }

  async function update2BSCertificate(dbs: DBSCertificate) {
    const data = await prompt(
      "Mise à jour certificat 2BS",
      "Veuillez sélectionner un nouveau certificat pour remplacer l'ancien.",
      DBSPrompt
    )

    if (entityID && data) {
      resolveUpdate2BS(entityID, dbs.certificate_id, data.certificate_id).then(
        () => {
          refresh()
          productionSites.refresh()
        }
      )
    }
  }

  useEffect(() => {
    if (entityID) {
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
