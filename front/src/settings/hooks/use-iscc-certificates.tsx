import { useEffect } from "react"
import { useTranslation } from "react-i18next"

import { EntitySelection } from "carbure/hooks/use-entity"
import { Certificate } from "common/types"

import { confirm, prompt } from "common/components/dialog"
import * as api from "../api"
import useAPI from "common/hooks/use-api"
import { CertificatePrompt } from "../components/certificates"
import { ProductionSiteSettingsHook } from "./use-production-sites"
import { useNotificationContext } from "common/components/notifications"
import { findISCCCertificates } from "common/api"
import { CompanySettingsHook } from "./use-company"

export interface ISCCCertificateSettingsHook {
  isEmpty: boolean
  isLoading: boolean
  certificates: Certificate[]
  addISCCCertificate: () => void
  deleteISCCCertificate: (d: Certificate) => void
  updateISCCCertificate: (d: Certificate) => void
}

export default function useISCCCertificates(
  entity: EntitySelection,
  productionSites: ProductionSiteSettingsHook,
  company: CompanySettingsHook
): ISCCCertificateSettingsHook {
  const { t } = useTranslation()
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
    if (typeof entityID !== "undefined") {
      resolveGetISCC(entityID)
      productionSites.refresh && productionSites.refresh()
      company.refresh && company.refresh()
    }
  }

  async function notifyCertificate(promise: Promise<any>, action: string) {
    const res = await promise

    if (res) {
      refresh()

      notifications.push({
        level: "success",
        text: t("Le certificat a bien été {{action}} !", { action }),
      })
    } else {
      notifications.push({
        level: "error",
        text: t("Le certificat n'a pas pu être {{action}}.", { action }),
      })
    }
  }

  async function addISCCCertificate() {
    const data = await prompt<Certificate>((resolve) => (
      <CertificatePrompt
        type="ISCC"
        title={t("Ajout certificat ISCC")}
        description={t("Vous pouvez rechercher parmi les certificats recensés sur Carbure et ajouter celui qui vous correspond.")} // prettier-ignore
        findCertificates={findISCCCertificates}
        onResolve={resolve}
      />
    ))

    if (typeof entityID !== "undefined" && data) {
      await notifyCertificate(
        resolveAddISCC(entityID, data.certificate_id),
        t("ajouté")
      )
    }
  }

  async function deleteISCCCertificate(iscc: Certificate) {
    if (
      typeof entityID !== "undefined" &&
      (await confirm(
        t("Suppression certificat"),
        t("Voulez-vous vraiment supprimer le certificat ISCC {{cert}} ?", { cert: iscc.certificate_id }) // prettier-ignore
      ))
    ) {
      await notifyCertificate(
        resolveDelISCC(entityID, iscc.certificate_id),
        t("supprimé")
      )
    }
  }

  async function updateISCCCertificate(iscc: Certificate) {
    const data = await prompt<Certificate>((resolve) => (
      <CertificatePrompt
        type="ISCC"
        title={t("Mise à jour certificat ISCC")}
        description={t("Veuillez sélectionner un nouveau certificat pour remplacer l'ancien.")} // prettier-ignore
        findCertificates={findISCCCertificates}
        onResolve={resolve}
      />
    ))

    if (typeof entityID !== "undefined" && data) {
      await notifyCertificate(
        resolveUpdateISCC(entityID, iscc.certificate_id, data.certificate_id),
        t("mis à jour")
      )
    }
  }

  useEffect(() => {
    if (typeof entityID !== "undefined") {
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
