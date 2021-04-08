import { EntitySelection } from "carbure/hooks/use-entity"
import { SettingsGetter } from "./use-get-settings"

import useAPI from "common/hooks/use-api"
import * as api from "../api"

import { NationalSystemCertificatePrompt } from "../components/national-system-certificates"
import { prompt } from "common/components/dialog"
import { useNotificationContext } from "common/components/notifications"

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
    const certificate = await prompt<string>((resolve) => (
      <NationalSystemCertificatePrompt
        currentCertificate={certificateNumber}
        onResolve={resolve}
      />
    ))

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
          text: `Impossible de modifier le n° de certificat - société non éligible`,
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
