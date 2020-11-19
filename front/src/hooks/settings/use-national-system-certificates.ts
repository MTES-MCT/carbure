import { EntitySelection } from "../helpers/use-entity"

import useAPI from "../helpers/use-api"
import * as api from "../../services/settings"

import { NationalSystemCertificatesPromptFactory } from "../../components/settings/national-system-certificates-settings"
import { prompt } from "../../components/system/dialog"
import { SettingsGetter } from "../use-app"

export interface NationalSystemCertificatesSettingsHook {
  isLoading: boolean
  certificateNumber: string
  editNationalSystemCertificates: () => void
}

export default function useNationalSystemCertificates(
  entity: EntitySelection,
  settings: SettingsGetter
): NationalSystemCertificatesSettingsHook {
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
      await resolveSetNSC(entity.id, certificate)
      settings.resolve()
    }
  }

  return {
    isLoading,
    certificateNumber,
    editNationalSystemCertificates,
  }
}
