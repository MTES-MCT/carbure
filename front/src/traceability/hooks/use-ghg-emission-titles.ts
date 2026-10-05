import { useTranslation } from "react-i18next"

export function useGhgEmissionTitles() {
  const { t } = useTranslation()

  return {
    eec: t(
      "Émissions résultant de l'extraction ou de la culture des matières premières"
    ),
    el: t(
      "Émissions annualisées résultant de modifications des stocks de carbone dues à des changements dans l'affectation des sols"
    ),
    ei: t("Émissions liées aux intrants"),
    ep: t("Émissions résultant de la transformation"),
    etd: t("Émissions résultant du transport et de la distribution"),
    eu: t("Émissions résultant du carburant à l'usage"),
    ecel: t(
      "Émissions résultant de la combustion de biomasse pour la production d'électricité"
    ),
    ech: t(
      "Émissions résultant de la combustion de biomasse pour la production de chaleur"
    ),
    esca: t(
      "Réductions d'émissions dues à l'accumulation du carbone dans les sols grâce à une meilleure gestion agricole"
    ),
    eccs: t(
      "Réductions d'émissions dues au piégeage et au stockage géologique du carbone"
    ),
    eccr: t(
      "Réductions d'émissions dues au piégeage et à la substitution du carbone"
    ),
    eee: t(
      "Réductions d'émissions dues à la production excédentaire d'électricité dans le cadre de la cogénération"
    ),
  }
}

export type GhgEmissionCode = keyof ReturnType<typeof useGhgEmissionTitles>
