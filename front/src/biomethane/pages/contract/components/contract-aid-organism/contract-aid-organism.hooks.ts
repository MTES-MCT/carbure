import { useTranslation } from "react-i18next"
import { ComplementaryAidOrganisms } from "biomethane/pages/contract/types"

export const useContractAidOrganismOptions = () => {
  const { t } = useTranslation()
  return [
    {
      label: t("Ademe"),
      value: ComplementaryAidOrganisms.ADEME,
    },
    {
      label: t("Région"),
      value: ComplementaryAidOrganisms.REGION,
    },
    {
      label: t("Autre"),
      value: ComplementaryAidOrganisms.OTHER,
    },
  ]
}
