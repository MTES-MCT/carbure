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

export const RecapData = {
  TeneurDeclaredMonth: RecapDataTeneurDeclaredMonth,
  QuantityAvailable: RecapDataQuantityAvailable,
}
