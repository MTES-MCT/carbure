import { useTranslation } from "react-i18next"
import Badge from "@codegouvfr/react-dsfr/Badge"
import { ReactNode } from "react"
import { useAnnualDeclarationTiruert } from "accounting/providers/annual-declaration-tiruert.provider"
import { formatEnergyNumber } from "accounting/utils/formatters"
import { formatNumber } from "common/utils/formatters"
import { CardProgress } from "../../card-progress"
import { CategoryObjective, TargetType } from "../../../types"
import { formatObjectiveGJ } from "../../../utils/objectives"
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
    if (category.is_objective_met) {
      badge = (
        <Badge severity="error" small>
          {t("Plafond atteint")}
        </Badge>
      )
    }
  } else {
    badge = (
      <CardProgress.DefaultBadge
        targetQuantity={progress.target}
        declaredQuantity={progress.total_teneur_declared}
      />
    )
  }

  return (
    <CardProgress
      title={category.code}
      mainValue={formatEnergyNumber(progress.total_teneur_declared)}
      mainText={t("GJ")}
      description={t(
        "Objectif en GJ en {{date}}: {{objective}} ({{target_percent}}% du total)",
        {
          date: selectedYear,
          objective: formatObjectiveGJ(progress.target),
          target_percent: formatNumber(category.target_percent ?? 0),
        }
      )}
      baseQuantity={category.teneur_declared_mj}
      targetQuantity={category.target_mj ?? 0}
      declaredQuantity={category.pending_teneur_mj}
      badge={badge}
      penalty={category.penalty}
      onClick={
        readOnly ||
        !isDeclarationInCurrentPeriod ||
        (isCapped && category.is_objective_met)
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
