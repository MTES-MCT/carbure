import { useEffect } from "react"
import { DBSPrompt } from "../../components/settings/2bs-certificates-settings"
import { confirm, prompt } from "../../components/system/dialog"
import * as api from "../../services/settings"
import { DBSCertificate } from "../../services/types"
import useAPI from "../helpers/use-api"
import { EntitySelection } from "../helpers/use-entity"

export interface DBSCertificateSettingsHook {
  isEmpty: boolean
  isLoading: boolean
  certificates: DBSCertificate[]
  add2BSCertificate: () => void
  delete2BSCertificate: (d: DBSCertificate) => void
}

export default function use2BSCertificates(
  entity: EntitySelection
): DBSCertificateSettingsHook {
  const [requestGet2BS, resolveGet2BS] = useAPI(api.get2BSCertificates)
  const [requestAdd2BS, resolveAdd2BS] = useAPI(api.add2BSCertificate)
  const [requestDel2BS, resolveDel2BS] = useAPI(api.delete2BSCertificate)

  const entityID = entity?.id
  const certificates = requestGet2BS.data ?? []

  const isLoading =
    requestGet2BS.loading || requestAdd2BS.loading || requestDel2BS.loading

  const isEmpty = certificates.length === 0

  function refresh() {
    if (entityID) {
      resolveGet2BS(entityID)
    }
  }

  async function add2BSCertificate() {
    const data = await prompt(
      "Ajouter un certificat 2BS",
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
      resolveDel2BS(entityID, dbs.certificate_id).then(refresh)
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
  }
}
