import { useTranslation } from "react-i18next"
import Badge from "@codegouvfr/react-dsfr/Badge"
import { ReactNode } from "react"
import { useAnnualDeclarationTiruert } from "accounting/providers/annual-declaration-tiruert.provider"
import { formatNumber } from "common/utils/formatters"
import { CardProgress } from "../../card-progress"
import { CategoryObjective, TargetType } from "../../../types"
import { formatObjectiveGJ } from "../../../utils/formatters"
import { ObjectiveProgressRecap } from "../objective-progress-recap"

type CategoryObjectiveProgressCardProps = {
  category: CategoryObjective
  readOnly: boolean
  onCategoryClick: (category: CategoryObjective, targetType: TargetType) => void
}

export const CategoryObjectiveProgressCard = ({
  category,
  readOnly,
  onCategoryClick,
}: CategoryObjectiveProgressCardProps) => {
  const { t } = useTranslation()
  const { selectedYear, isDeclarationInCurrentPeriod } =
    useAnnualDeclarationTiruert()
  const { progress } = category
  const isCapped = category.target_type === TargetType.CAP

  let badge: ReactNode = null

  if (isCapped) {
    if (progress.is_objective_met) {
      badge = (
        <Badge severity="error" small>
          {t("Plafond atteint")}
        </Badge>
      )
    }
  } else {
    badge = (
      <CardProgress.DefaultBadge
        targetQuantity={progress.target_quantity}
        declaredQuantity={progress.total_teneur_declared}
      />
    )
  }

  return (
    <CardProgress
      title={category.code}
      mainValue={formatNumber(progress.total_teneur_declared, {
        fractionDigits: 2,
      })}
      mainText={t("GJ")}
      description={t(
        "Objectif en GJ en {{date}}: {{objective}} ({{target_percent}}% du total)",
        {
          date: selectedYear,
          objective: formatObjectiveGJ(progress.target_quantity),
          target_percent: formatNumber(category.target_percent),
        }
      )}
      baseQuantity={progress.base_quantity}
      targetQuantity={progress.target_quantity}
      declaredQuantity={progress.declared_quantity}
      badge={badge}
      penalty={category.penalty}
      onClick={
        readOnly ||
        !isDeclarationInCurrentPeriod ||
        (isCapped && progress.is_objective_met)
          ? undefined
          : () => onCategoryClick(category, category.target_type!)
      }
    >
      {isDeclarationInCurrentPeriod && (
        <ObjectiveProgressRecap
          objective={category}
          remainingType={isCapped ? "limit" : "objective"}
        />
      )}
    </CardProgress>
  )
}
