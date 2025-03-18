import { Text } from "common/components/text"
import { useTranslation } from "react-i18next"

const RecapDataTeneurDeclaredMonth = ({
  value,
  unit,
}: {
  value: number
  unit: string
}) => {
  const { t } = useTranslation()
  return (
    <Text is="li" size="sm">
      {t("Teneur déclarée ce mois :")}{" "}
      {t("{{count}} {{unit}}", {
        count: value,
        unit,
      })}
    </Text>
  )
}

const RecapDataTeneurDeclared = ({
  value,
  unit,
}: {
  value: number
  unit: string
}) => {
  const { t } = useTranslation()
  return (
    <Text is="li" size="sm">
      {t("Teneur totale déclarée :")}{" "}
      {t("{{count}} {{unit}}", {
        count: value,
        unit,
      })}
    </Text>
  )
}

const RecapDataQuantityAvailable = ({
  value,
  unit,
}: {
  value: number
  unit: string
}) => {
  const { t } = useTranslation()
  return (
    <Text is="li" size="sm">
      {t("Volume disponible :")}{" "}
      {t("{{count}} {{unit}}", { count: value, unit })}
    </Text>
  )
}

const RemainingQuantityBeforeLimit = ({
  value,
  unit,
}: {
  value: number
  unit: string
}) => {
  const { t } = useTranslation()
  return (
    <Text is="li" size="sm">
      {t("Volume restant jusqu’au plafond :")}{" "}
      {t("{{count}} {{unit}}", { count: value, unit })}
    </Text>
  )
}

const RemainingQuantityBeforeObjective = ({
  value,
  unit,
}: {
  value: number
  unit: string
}) => {
  const { t } = useTranslation()
  return (
    <Text is="li" size="sm">
      {t("Volume restant jusqu’à l’objectif :")}{" "}
      {t("{{count}} {{unit}}", { count: value, unit })}
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
