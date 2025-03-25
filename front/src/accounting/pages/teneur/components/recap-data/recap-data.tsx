import { Text } from "common/components/text"
import { useTranslation } from "react-i18next"

const RecapDataTeneurDeclaredMonth = ({ value }: { value: string }) => {
  const { t } = useTranslation()
  return (
    <Text size="sm">
      {t("Teneur déclarée ce mois :")}{" "}
      {t("{{value}}", {
        value,
      })}
    </Text>
  )
}

const RecapDataTeneurDeclared = ({ value }: { value: string }) => {
  const { t } = useTranslation()
  return (
    <Text size="sm">
      {t("Teneur totale déclarée :")}{" "}
      {t("{{value}}", {
        value,
      })}
    </Text>
  )
}

const RecapDataQuantityAvailable = ({ value }: { value: string }) => {
  const { t } = useTranslation()
  return (
    <Text size="sm">
      {t("Volume disponible :")} {t("{{value}}", { value })}
    </Text>
  )
}

const RemainingQuantityBeforeLimit = ({ value }: { value: string }) => {
  const { t } = useTranslation()
  return (
    <Text size="sm">
      {t("Volume restant jusqu’au plafond :")} {t("{{value}}", { value })}
    </Text>
  )
}

const RemainingQuantityBeforeObjective = ({ value }: { value: string }) => {
  const { t } = useTranslation()
  return (
    <Text size="sm">
      {t("Volume restant jusqu’à l’objectif :")} {t("{{value}}", { value })}
    </Text>
  )
}

export const RecapData = {
  TeneurDeclared: RecapDataTeneurDeclared,
  TeneurDeclaredMonth: RecapDataTeneurDeclaredMonth,
  QuantityAvailable: RecapDataQuantityAvailable,
  RemainingQuantityBeforeLimit: RemainingQuantityBeforeLimit,
  RemainingQuantityBeforeObjective: RemainingQuantityBeforeObjective,
}
