import { MainObjective } from "../../../types"
import { CardProgress } from "../../card-progress"
import { ObjectiveSection } from "../objective-section"
import { Trans, useTranslation } from "react-i18next"
import { formatNumber } from "common/utils/formatters"
import { useAnnualDeclarationTiruert } from "accounting/providers/annual-declaration-tiruert.provider"
import { ObjectiveProgressRecap } from "../objective-progress-recap"
import { ExtendedUnit } from "common/types"
import { formatEnergyNumber } from "accounting/utils/formatters"

type OverallProgressProps = {
  objective?: MainObjective
}

export const OverallProgress = ({ objective }: OverallProgressProps) => {
  const { t } = useTranslation()
  const { selectedYear, isDeclarationInCurrentPeriod } =
    useAnnualDeclarationTiruert()

  return (
    <ObjectiveSection
      title={t("Avancement global")}
      description={
        <Trans
          i18nKey="Base calculée : {{energy_basis}} GJ"
          values={{
            energy_basis: formatEnergyNumber(objective?.energy_basis ?? 0),
          }}
        />
      }
    >
      {objective && (
        <CardProgress
          title={t("Année {{year}}", {
            year: selectedYear,
          })}
          description={t(
            "Objectif {{date}}: {{objective}} tCO2 évitées ({{target_percent}}% du total)",
            {
              date: selectedYear,
              objective: formatNumber(objective.target, {
                fractionDigits: 0,
                mode: "ceil",
              }),
              target_percent: formatNumber(objective.target_percent),
            }
          )}
          mainValue={formatNumber(
            objective.teneur_declared + objective.pending_teneur,
            {
              fractionDigits: 0,
            }
          )}
          mainText={t("tCO2 évitées")}
          baseQuantity={objective.progress.base_quantity}
          targetQuantity={objective.progress.target_quantity}
          declaredQuantity={objective.progress.declared_quantity}
          badge={
            <CardProgress.DefaultBadge
              targetQuantity={objective.target}
              declaredQuantity={
                objective.teneur_declared + objective.pending_teneur
              }
            />
          }
          penalty={objective.penalty}
        >
          {isDeclarationInCurrentPeriod && (
            <ObjectiveProgressRecap
              objective={objective}
              remainingType="objective"
              unit={ExtendedUnit.tCO2ev}
            />
          )}
        </CardProgress>
      )}
    </ObjectiveSection>
  )
}
