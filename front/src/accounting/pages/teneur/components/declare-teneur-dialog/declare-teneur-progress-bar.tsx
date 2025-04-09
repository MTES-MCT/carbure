import { Text } from "common/components/text"
import { useTranslation } from "react-i18next"
import { ProgressBar } from "../progress-bar"
import { SectorObjective, TargetType } from "../../types"
import { ceilNumber, floorNumber } from "common/utils/formatters"
import { formatSector } from "accounting/utils/formatters"

interface DeclareTeneurProgressBarProps {
  teneurDeclared: number
  teneurDeclaredMonth: number
  target: number
  quantity: number
  targetType?: TargetType
  sector?: SectorObjective["code"]
}
export const DeclareTeneurProgressBar = ({
  teneurDeclared,
  teneurDeclaredMonth,
  target,
  quantity,
  targetType,
  sector,
}: DeclareTeneurProgressBarProps) => {
  const { t } = useTranslation()
  const formatNumber =
    targetType && targetType === TargetType.REACH ? ceilNumber : floorNumber

  return (
    <>
      <Text>
        {sector
          ? t("Rappel de votre progression pour la filière {{sector}}", {
              sector: formatSector(sector),
            })
          : t("Rappel de votre progression")}
      </Text>
      <ProgressBar
        baseQuantity={formatNumber(teneurDeclared, 0)}
        targetQuantity={formatNumber(target, 0)}
        declaredQuantity={formatNumber(
          teneurDeclaredMonth + (quantity ?? 0),
          0
        )}
      />
    </>
  )
}
