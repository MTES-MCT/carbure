import { EntitySelection } from "../../common/hooks/helpers/use-entity"

import useAPI from "../../common/hooks/helpers/use-api"
import * as api from "../api"

import { NationalSystemCertificatesPromptFactory } from "../components/national-system-certificates-settings"
import { prompt } from "../../common/system/dialog"
import { SettingsGetter } from "../../carbure/hooks"
import { useNotificationContext } from "../../common/system/notifications"

export interface NationalSystemCertificatesSettingsHook {
  isLoading: boolean
  certificateNumber: string
  editNationalSystemCertificates: () => void
}

export default function useNationalSystemCertificates(
  entity: EntitySelection,
  settings: SettingsGetter
): NationalSystemCertificatesSettingsHook {
  const notifications = useNotificationContext()

  const [requestSetNSC, resolveSetNSC] = useAPI(
    api.setNationalSystemCertificate
  )

  const isLoading = requestSetNSC.loading || settings.loading
  const certificateNumber = entity?.national_system_certificate ?? ""

  async function editNationalSystemCertificates() {
    const certificate = await prompt(
      "Modifier n° de certificat",
      "Entrez votre numéro de certificat du Système National",
      NationalSystemCertificatesPromptFactory(certificateNumber)
    )

    if (entity && certificate) {
      const res = await resolveSetNSC(entity.id, certificate)

      if (res) {
        settings.resolve()

        notifications.push({
          level: "success",
          text: "Le n° de certificat a bien été modifié !",
        })
      } else {
        notifications.push({
          level: "error",
          text: "Impossible de modifier le n° de certificat.",
        })
      }
    }
  }

  return {
    isLoading,
    certificateNumber,
    editNationalSystemCertificates,
  }
}
