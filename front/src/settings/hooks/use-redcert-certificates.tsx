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
import { findREDCertCertificates } from "common/api"
import { CompanySettingsHook } from "./use-company"

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
  productionSites: ProductionSiteSettingsHook,
  company: CompanySettingsHook
): REDCertCertificateSettingsHook {
  const { t } = useTranslation()
  const notifications = useNotificationContext()

  const [requestGetREDCert, resolveGetREDCert] = useAPI(
    api.getREDCertCertificates
  )
  const [requestAddREDCert, resolveAddREDCert] = useAPI(
    api.addREDCertCertificate
  )
  const [requestDelREDCert, resolveDelREDCert] = useAPI(
    api.deleteREDCertCertificate
  )
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

  async function addREDCertCertificate() {
    const data = await prompt<Certificate>((resolve) => (
      <CertificatePrompt
        type="REDcert"
        title={t("Ajout certificat REDcert")}
        description={t("Vous pouvez rechercher parmi les certificats recensés sur Carbure et ajouter celui qui vous correspond.")} // prettier-ignore
        findCertificates={findREDCertCertificates}
        onResolve={resolve}
      />
    ))

    if (typeof entityID !== "undefined" && data) {
      await notifyCertificate(
        resolveAddREDCert(entityID, data.certificate_id),
        t("ajouté")
      )
    }
  }

  async function deleteREDCertCertificate(redcert: Certificate) {
    if (
      typeof entityID !== "undefined" &&
      (await confirm(
        t("Suppression certificat"),
        t("Voulez-vous vraiment supprimer le certificat REDcert {{cert}} ?", { cert: redcert.certificate_id }) // prettier-ignore
      ))
    ) {
      await notifyCertificate(
        resolveDelREDCert(entityID, redcert.certificate_id),
        t("supprimé")
      )
    }
  }

  async function updateREDCertCertificate(iscc: Certificate) {
    const data = await prompt<Certificate>((resolve) => (
      <CertificatePrompt
        type="REDcert"
        title={t("Mise à jour certificat REDcert")}
        description={t("Veuillez sélectionner un nouveau certificat pour remplacer l'ancien.")} // prettier-ignore
        findCertificates={findREDCertCertificates}
        onResolve={resolve}
      />
    ))

    if (typeof entityID !== "undefined" && data) {
      await notifyCertificate(
        resolveUpdateREDCert(
          entityID,
          iscc.certificate_id,
          data.certificate_id
        ),
        t("mis à jour")
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
