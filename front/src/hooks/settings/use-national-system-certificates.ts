import { NationalSystemCertificatesPrompt } from "../../components/settings/national-system-certificates-settings"
import { prompt } from "../../components/system/dialog"
import { EntitySelection } from "../helpers/use-entity"

export interface NationalSystemCertificatesSettingsHook {
  isLoading: boolean
  certificateNumber: string
  editNationalSystemCertificates: () => void
}

export default function useNationalSystemCertificates(
  entity: EntitySelection
): NationalSystemCertificatesSettingsHook {
  const isLoading = false
  const certificateNumber = ""

  async function editNationalSystemCertificates() {
    const certificate = await prompt(
      "Modifier n° de certificat",
      "Entrez votre numéro de certificat du Système National",
      NationalSystemCertificatesPrompt
    )

    if (certificate) {
      // @TODO call the api to update number
    }
  }

  return {
    isLoading,
    certificateNumber,
    editNationalSystemCertificates,
  }
}
