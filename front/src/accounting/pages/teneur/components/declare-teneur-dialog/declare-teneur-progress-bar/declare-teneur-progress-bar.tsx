import { useTranslation } from "react-i18next"
import { RecapData } from "../../recap-data"
import {
  CategoryObjective,
  SectorObjective,
  TargetType,
  UnconstrainedCategoryObjective,
} from "../../../types"
import { floorNumber } from "common/utils/formatters"
import { formatSector } from "accounting/utils/formatters"
import { ReactNode } from "react"
import Badge from "@codegouvfr/react-dsfr/Badge"
import { Grid } from "common/components/scaffold"
import { CategoryEnum } from "common/types"
import {
  computeRemainingEnergyWithAdditionalQuantity,
  formatObjectiveGJ,
} from "../../../utils/formatters"
import { ProgressBar } from "../../progress-bar"

interface DeclareTeneurProgressBarProps {
  teneurDeclared: number
  pendingTeneur: number
  target: number
  quantity: number
  label?: ReactNode
  targetType?: TargetType
  category?: CategoryEnum
  description?: ReactNode
  formatRemaining?: (value: number) => string
}

export const DeclareTeneurProgressBar = ({
  teneurDeclared,
  pendingTeneur,
  target,
  quantity,
  label,
  targetType,
  category,
  formatRemaining = formatObjectiveGJ,
}: DeclareTeneurProgressBarProps) => {
  console.log("calculating remaining energy with additional quantity", {
    target,
    teneurDeclared,
    pendingTeneur,
    quantity,
  })
  const remainingEnergy = targetType
    ? computeRemainingEnergyWithAdditionalQuantity(
        {
          target,
          teneur_declared: teneurDeclared,
          pending_teneur: pendingTeneur,
        },
        quantity ?? 0
      )
    : null

  const RemainingQuantity =
    targetType === TargetType.CAP
      ? RecapData.RemainingQuantityBeforeLimit
      : RecapData.RemainingQuantityBeforeObjective

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "var(--spacing-1v)",
      }}
    >
      {label && (
        <Badge severity="info" small noIcon>
          {label}
        </Badge>
      )}
      <ProgressBar
        baseQuantity={floorNumber(teneurDeclared, 0)}
        targetQuantity={floorNumber(target, 0)}
        declaredQuantity={floorNumber(pendingTeneur + (quantity ?? 0), 0)}
      />
      {targetType && remainingEnergy !== null && (
        <RemainingQuantity
          value={formatRemaining(remainingEnergy)}
          bold
          size="md"
          category={category}
        />
      )}
    </div>
  )
}

type DeclareTeneurProgressBarListProps = {
  sectorObjective?: SectorObjective
  categoryObjective?: CategoryObjective | UnconstrainedCategoryObjective
  quantity: number
  targetType?: TargetType
}

export const DeclareTeneurProgressBarList = ({
  sectorObjective,
  categoryObjective,
  quantity,
  targetType,
}: DeclareTeneurProgressBarListProps) => {
  const { t } = useTranslation()

  return (
    <Grid gap="xl">
      {categoryObjective?.target && targetType && (
        <DeclareTeneurProgressBar
          teneurDeclared={categoryObjective.teneur_declared}
          pendingTeneur={categoryObjective.pending_teneur}
          target={categoryObjective.target}
          quantity={quantity ?? 0}
          label={t("Catégorie {{category}}", {
            category: categoryObjective.code,
          })}
          targetType={targetType}
          category={categoryObjective.code}
        />
      )}
      {sectorObjective && (
        <DeclareTeneurProgressBar
          teneurDeclared={sectorObjective.teneur_declared}
          pendingTeneur={sectorObjective.pending_teneur}
          target={sectorObjective.target}
          quantity={quantity ?? 0}
          label={t("Filière {{sector}}", {
            sector: formatSector(sectorObjective.code),
          })}
          targetType={TargetType.REACH}
        />
      )}
    </Grid>
  )
}
