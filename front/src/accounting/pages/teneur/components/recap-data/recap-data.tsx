import { Text } from "common/components/text"
import { useTranslation } from "react-i18next"

const RecapDataTeneurDeclaredMonth = ({ value }: { value: string }) => {
  const { t } = useTranslation()
  return (
    <Text size="sm">
      {t("Teneur déclarée ce mois :")} {value}
    </Text>
  )
}

const RecapDataTeneurDeclared = ({ value }: { value: string }) => {
  const { t } = useTranslation()
  return (
    <Text size="sm">
      {t("Teneur totale déclarée :")} {value}
    </Text>
  )
}

const RecapDataQuantityAvailable = ({ value }: { value: string }) => {
  const { t } = useTranslation()
  return (
    <Text size="sm">
      {t("Quantité disponible :")} {value}
    </Text>
  )
}

const RemainingQuantityBeforeLimit = ({ value }: { value: string }) => {
  const { t } = useTranslation()
  return (
    <Text size="sm">
      {t("Quantité restante jusqu’au plafond :")} {value}
    </Text>
  )
}

const RemainingQuantityBeforeObjective = ({ value }: { value: string }) => {
  const { t } = useTranslation()
  return (
    <Text size="sm">
      {t("Quantité restante jusqu’à l’objectif :")} {value}
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
