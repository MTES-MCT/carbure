import { useTranslation } from "react-i18next"
import { formatSector } from "accounting/utils/formatters"
import { CardProgress } from "../../card-progress"
import { ObjectiveSection } from "../objective-section"
import { SectorObjective } from "../../../types"
import { CardGrid } from "../../card-grid"
import { formatNumber } from "common/utils/formatters"
import { useAnnualDeclarationTiruert } from "accounting/providers/annual-declaration-tiruert.provider"
import { formatObjectiveGJ } from "../../../utils/formatters"
import { ObjectiveProgressRecap } from "../objective-progress-recap"

type SectorProgressProps = {
  sectors?: SectorObjective[]
}

export const SectorProgress = ({ sectors }: SectorProgressProps) => {
  const { t } = useTranslation()
  const { selectedYear, isDeclarationInCurrentPeriod } =
    useAnnualDeclarationTiruert()

  return (
    <ObjectiveSection
      title={t("Avancement par filière")}
      description={t("Retrouvez ici votre suivi d'objectif par filière.")}
    >
      <CardGrid>
        {sectors?.map((sector) => {
          const { progress } = sector

          return (
            <CardProgress
              key={sector.code}
              title={formatSector(sector.code)}
              description={t(
                "Objectif en GJ en {{date}}: {{objective}} ({{target_percent}}% du total pour cette catégorie)",
                {
                  date: selectedYear,
                  objective: formatObjectiveGJ(sector.target),
                  target_percent: formatNumber(sector.target_percent),
                }
              )}
              mainValue={formatNumber(progress.total_teneur_declared, {
                fractionDigits: 0,
              })}
              mainText={t("GJ")}
              baseQuantity={progress.base_quantity}
              targetQuantity={progress.target_quantity}
              declaredQuantity={progress.declared_quantity}
              badge={
                <CardProgress.DefaultBadge
                  targetQuantity={progress.target_quantity}
                  declaredQuantity={progress.total_teneur_declared}
                />
              }
              penalty={sector.penalty}
            >
              {isDeclarationInCurrentPeriod && (
                <ObjectiveProgressRecap
                  objective={sector}
                  remainingType="objective"
                />
              )}
            </CardProgress>
          )
        })}
      </CardGrid>
    </ObjectiveSection>
  )
}
