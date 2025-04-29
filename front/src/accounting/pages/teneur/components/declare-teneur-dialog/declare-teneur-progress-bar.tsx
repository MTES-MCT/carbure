import { useTranslation } from "react-i18next"
import { ProgressBar } from "../progress-bar"
import {
  CategoryObjective,
  SectorObjective,
  TargetType,
  UnconstrainedCategoryObjective,
} from "../../types"
import { floorNumber } from "common/utils/formatters"
import { formatSector } from "accounting/utils/formatters"
import { ReactNode } from "react"
import Badge from "@codegouvfr/react-dsfr/Badge"
import { Grid } from "common/components/scaffold"

interface DeclareTeneurProgressBarProps {
  teneurDeclared: number
  teneurDeclaredMonth: number
  target: number
  quantity: number
  targetType?: TargetType
  label?: ReactNode
}
export const DeclareTeneurProgressBar = ({
  teneurDeclared,
  teneurDeclaredMonth,
  target,
  quantity,
  label,
}: DeclareTeneurProgressBarProps) => {
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
        declaredQuantity={floorNumber(teneurDeclaredMonth + (quantity ?? 0), 0)}
      />
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
      {categoryObjective && categoryObjective.target && (
        <DeclareTeneurProgressBar
          teneurDeclared={categoryObjective.teneur_declared}
          teneurDeclaredMonth={categoryObjective.teneur_declared_month}
          target={categoryObjective.target}
          quantity={quantity ?? 0}
          targetType={targetType}
          label={t("Catégorie {{category}}", {
            category: categoryObjective.code,
          })}
        />
      )}
      {sectorObjective && (
        <DeclareTeneurProgressBar
          teneurDeclared={sectorObjective?.teneur_declared ?? 0}
          teneurDeclaredMonth={sectorObjective?.teneur_declared_month ?? 0}
          target={sectorObjective?.target ?? 0}
          quantity={quantity ?? 0}
          label={t("Filière {{sector}}", {
            sector: formatSector(sectorObjective?.code),
          })}
          targetType={targetType}
        />
      )}
    </Grid>
  )
}
