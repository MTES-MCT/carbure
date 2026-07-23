import { useTranslation } from "react-i18next"
import { RecapData } from "../../recap-data"
import {
  CategoryObjective,
  EnergyObjective,
  SectorObjective,
  TargetType,
  UnconstrainedCategoryObjective,
} from "../../../types"
import { formatSector } from "accounting/utils/formatters"
import { ReactNode } from "react"
import Badge from "@codegouvfr/react-dsfr/Badge"
import { Grid } from "common/components/scaffold"
import { CategoryEnum } from "common/types"
import {
  formatObjectiveCO2,
  formatObjectiveGJ,
  remainingGjAfterAdditionalMj,
} from "../../../utils/formatters"
import { remainingMj } from "../../../utils/energy"
import { ProgressBar } from "../../progress-bar"

const containerStyle = {
  display: "flex",
  flexDirection: "column" as const,
  gap: "var(--spacing-1v)",
}

type TeneurProgressBarSectionProps = {
  label?: ReactNode
  targetType?: TargetType
  category?: CategoryEnum
  baseQuantity: number
  targetQuantity: number
  declaredQuantity: number
  remaining?: number | null
  formatRemaining?: (value: number) => string
}

const TeneurProgressBarSection = ({
  label,
  targetType,
  category,
  baseQuantity,
  targetQuantity,
  declaredQuantity,
  remaining,
  formatRemaining = formatObjectiveGJ,
}: TeneurProgressBarSectionProps) => {
  const RemainingQuantity =
    targetType === TargetType.CAP
      ? RecapData.RemainingQuantityBeforeLimit
      : RecapData.RemainingQuantityBeforeObjective

  return (
    <div style={containerStyle}>
      {label && (
        <Badge severity="info" small noIcon>
          {label}
        </Badge>
      )}
      <ProgressBar
        baseQuantity={baseQuantity}
        targetQuantity={targetQuantity}
        declaredQuantity={declaredQuantity}
      />
      {targetType != null && remaining != null && (
        <RemainingQuantity
          value={formatRemaining(remaining)}
          bold
          size="md"
          category={category}
        />
      )}
    </div>
  )
}

type EnergyTeneurProgressBarProps = {
  objective: Pick<
    EnergyObjective,
    "target_mj" | "teneur_declared_mj" | "pending_teneur_mj"
  >
  additionalMj: number
  label?: ReactNode
  targetType?: TargetType
  category?: CategoryEnum
}

export const EnergyTeneurProgressBar = ({
  objective,
  additionalMj,
  label,
  targetType,
  category,
}: EnergyTeneurProgressBarProps) => (
  <TeneurProgressBarSection
    label={label}
    targetType={targetType}
    category={category}
    baseQuantity={objective.teneur_declared_mj}
    targetQuantity={objective.target_mj ?? 0}
    declaredQuantity={objective.pending_teneur_mj + additionalMj}
    remaining={
      targetType != null
        ? remainingGjAfterAdditionalMj(objective, additionalMj)
        : null
    }
  />
)

type Co2TeneurProgressBarProps = {
  teneurDeclared: number
  pendingTeneur: number
  target: number
  additionalQuantity: number
  label?: ReactNode
  targetType?: TargetType
  formatRemaining?: (value: number) => string
}

export const Co2TeneurProgressBar = ({
  teneurDeclared,
  pendingTeneur,
  target,
  additionalQuantity,
  label,
  targetType,
  formatRemaining = formatObjectiveCO2,
}: Co2TeneurProgressBarProps) => (
  <TeneurProgressBarSection
    label={label}
    targetType={targetType}
    baseQuantity={teneurDeclared}
    targetQuantity={target}
    declaredQuantity={pendingTeneur + additionalQuantity}
    remaining={
      targetType != null
        ? remainingMj(target, teneurDeclared, pendingTeneur, additionalQuantity)
        : null
    }
    formatRemaining={formatRemaining}
  />
)

type DeclareTeneurProgressBarListProps = {
  sectorObjective?: SectorObjective
  categoryObjective?: CategoryObjective | UnconstrainedCategoryObjective
  quantityMj: number
  targetType?: TargetType
}

export const DeclareTeneurProgressBarList = ({
  sectorObjective,
  categoryObjective,
  quantityMj,
  targetType,
}: DeclareTeneurProgressBarListProps) => {
  const { t } = useTranslation()

  return (
    <Grid gap="xl">
      {categoryObjective?.target_mj && targetType && (
        <EnergyTeneurProgressBar
          objective={categoryObjective}
          additionalMj={quantityMj}
          label={t("Catégorie {{category}}", {
            category: categoryObjective.code,
          })}
          targetType={targetType}
          category={categoryObjective.code}
        />
      )}
      {sectorObjective && (
        <EnergyTeneurProgressBar
          objective={sectorObjective}
          additionalMj={quantityMj}
          label={t("Filière {{sector}}", {
            sector: formatSector(sectorObjective.code),
          })}
          targetType={TargetType.REACH}
        />
      )}
    </Grid>
  )
}
