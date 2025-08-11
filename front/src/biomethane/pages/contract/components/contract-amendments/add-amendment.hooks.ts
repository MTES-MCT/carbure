import { useTranslation } from "react-i18next"
import { AmendmentObjectEnum } from "api-schema"

export const useAddAmendmentObjectOptions = () => {
  const { t } = useTranslation()

  return [
    {
      label: t("Modification de la Cmax/PAP"),
      value: AmendmentObjectEnum.CMAX_PAP_UPDATE,
    },
    {
      label: t("Avenant fixant la date de prise d'effet"),
      value: AmendmentObjectEnum.EFFECTIVE_DATE,
    },
    {
      label: t("Annualisation de la Cmax"),
      value: AmendmentObjectEnum.CMAX_ANNUALIZATION,
    },
    {
      label: t("Modification des proportions de la prime intrant"),
      value: AmendmentObjectEnum.INPUT_BONUS_UPDATE,
    },
    {
      label: t("Modification de l'indexation L"),
      value: AmendmentObjectEnum.L_INDEXATION_UPDATE,
    },
    {
      label: t(
        "Changement des informations relatives au producteur/acheteur de biométhane"
      ),
      value: AmendmentObjectEnum.PRODUCER_BUYER_INFO_CHANGE,
    },
    {
      label: t(
        "Modification des conditions d'efficacité énergétique et environnementale"
      ),
      value: AmendmentObjectEnum.ENERGY_ENVIRONMENTAL_EFFICIENCY_UPDATE,
    },
    {
      label: t("Autre"),
      value: AmendmentObjectEnum.OTHER,
    },
  ]
}
