import { TariffReference } from "biomethane/pages/contract/types"
import { useTranslation } from "react-i18next"

export const useAttestNoFossilForEnergy = (
  tariffReference?: TariffReference | null
) => {
  const { t } = useTranslation()
  const isTariffReference2023 = tariffReference === TariffReference.Value2023

  if (isTariffReference2023) {
    return {
      label: t(
        "J'atteste que les besoins en énergie cités ci-dessus ne sont pas satisfaits par une énergie d’origine fossile."
      ),
      hintText: t(
        "Notamment liés à la pasteurisation, l’hygiénisation et le prétraitement des intrants, le chauffage du digesteur et l’épuration du biogaz"
      ),
      legend: t(
        "Besoins en énergie de l’installation de production de biométhane"
      ),
    }
  }

  return {
    label: t(
      "J'atteste que les besoins en énergie cités ci-dessus ne sont pas satisfaits par une énergie d’origine fossile."
    ),
    hintText: t(
      "Pour une installation de méthanisation ainsi qu’à l’épuration du biogaz et à l’oxydation des évents"
    ),
    legend: t("Besoins en énergie liés au chauffage du digesteur"),
  }
}
