import { Text } from "common/components/text"
import { useTranslation } from "react-i18next"
import { ProgressBar } from "../progress-bar"
import {
  CategoryObjective,
  MainObjective,
  SectorObjective,
  TargetType,
  UnconstrainedCategoryObjective,
} from "../../types"
import { ceilNumber, floorNumber } from "common/utils/formatters"
import { formatSector } from "accounting/utils/formatters"
import { ReactNode } from "react"

interface DeclareTeneurProgressBarProps {
  teneurDeclared: number
  teneurDeclaredMonth: number
  target: number
  quantity: number
  targetType?: TargetType
  label?: ReactNode
}
const DeclareTeneurProgressBar = ({
  teneurDeclared,
  teneurDeclaredMonth,
  target,
  quantity,
  targetType,
  label,
}: DeclareTeneurProgressBarProps) => {
  const formatNumber =
    targetType && targetType === TargetType.REACH ? ceilNumber : floorNumber

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "var(--spacing-1v)",
      }}
    >
      {label && <Text size="sm">{label}</Text>}
      <ProgressBar
        baseQuantity={formatNumber(teneurDeclared, 0)}
        targetQuantity={formatNumber(target, 0)}
        declaredQuantity={formatNumber(
          teneurDeclaredMonth + (quantity ?? 0),
          0
        )}
      />
    </div>
  )
}

type DeclareTeneurProgressBarProps2 = {
  mainObjective: MainObjective
  sectorObjective?: SectorObjective
  categoryObjective?: CategoryObjective | UnconstrainedCategoryObjective
  quantity: number
  targetType?: TargetType
}
export const DeclareTeneurProgressBars = ({
  mainObjective,
  sectorObjective,
  categoryObjective,
  quantity,
  targetType,
}: DeclareTeneurProgressBarProps2) => {
  const { t } = useTranslation()
  return (
    <>
      <DeclareTeneurProgressBar
        teneurDeclared={mainObjective.teneur_declared}
        teneurDeclaredMonth={mainObjective.teneur_declared_month}
        target={mainObjective.target}
        quantity={quantity ?? 0}
        targetType={TargetType.REACH}
        label={t("Objectif global")}
      />
      {sectorObjective && (
        <DeclareTeneurProgressBar
          teneurDeclared={sectorObjective?.teneur_declared ?? 0}
          teneurDeclaredMonth={sectorObjective?.teneur_declared_month ?? 0}
          target={sectorObjective?.target ?? 0}
          quantity={quantity ?? 0}
          label={t("Objectif pour la filière {{sector}}", {
            sector: formatSector(sectorObjective?.code),
          })}
          targetType={targetType}
        />
      )}
      {categoryObjective && categoryObjective.target && (
        <DeclareTeneurProgressBar
          teneurDeclared={categoryObjective.teneur_declared}
          teneurDeclaredMonth={categoryObjective.teneur_declared_month}
          target={categoryObjective.target}
          quantity={quantity ?? 0}
          targetType={targetType}
          label={t("Objectif pour la catégorie {{category}}", {
            category: categoryObjective.code,
          })}
        />
      )}
    </>
  )
}
