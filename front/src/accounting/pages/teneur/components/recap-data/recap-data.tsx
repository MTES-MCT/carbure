import { Text, TextProps } from "common/components/text"
import { CategoryEnum } from "common/types"
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

const RemainingQuantityBeforeLimit = ({
  value,
  bold,
  size = "sm",
  category,
}: {
  value: string
  bold?: boolean
  size?: TextProps<"p">["size"]
  category?: CategoryEnum
}) => {
  const { t } = useTranslation()
  return (
    <Text size={size} fontWeight={bold ? "bold" : "regular"}>
      {category
        ? t(
          "Quantité restante jusqu'au plafond pour la catégorie {{category}} :",
          {
            category,
          }
        )
        : t("Quantité restante jusqu’au plafond :")}{" "}
      {value}
    </Text>
  )
}

const RemainingQuantityBeforeObjective = ({
  value,
  bold,
  size = "sm",
  category,
}: {
  value: string
  bold?: boolean
  size?: TextProps<"p">["size"]
  category?: CategoryEnum
}) => {
  const { t } = useTranslation()
  return (
    <Text size={size} fontWeight={bold ? "bold" : "regular"}>
      {category
        ? t(
          "Quantité restante jusqu'à l'objectif pour la catégorie {{category}} :",
          {
            category,
          }
        )
        : t("Quantité restante jusqu’à l’objectif :")}{" "}
      {value}
    </Text>
  )
}

const RemainingQuantityBegoreCO2Objective = ({
  value,
  bold,
  size = "sm",
}: {
  value: string
  bold?: boolean
  size?: TextProps<"p">["size"]
}) => {
  const { t } = useTranslation()
  return (
    <Text size={size} fontWeight={bold ? "bold" : "regular"}>
      {t("Quantité restante jusqu'à l'objectif global CO2 :")} {value} tCO2 évitées
    </Text>
  )
}

export const RecapData = {
  TeneurDeclared: RecapDataTeneurDeclared,
  TeneurDeclaredMonth: RecapDataTeneurDeclaredMonth,
  QuantityAvailable: RecapDataQuantityAvailable,
  RemainingQuantityBeforeLimit: RemainingQuantityBeforeLimit,
  RemainingQuantityBeforeObjective: RemainingQuantityBeforeObjective,
  RemainingQuantityBegoreCO2Objective: RemainingQuantityBegoreCO2Objective,
}
