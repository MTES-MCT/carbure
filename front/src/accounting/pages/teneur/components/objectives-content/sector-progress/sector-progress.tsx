import { useTranslation } from "react-i18next"
import { formatEnergyNumber, formatSector } from "accounting/utils/formatters"
import { CardProgress } from "../../card-progress"
import { ObjectiveSection } from "../objective-section"
import { SectorObjective } from "../../../types"
import { CardGrid } from "../../card-grid"
import { formatNumber } from "common/utils/formatters"
import { useAnnualDeclarationTiruert } from "accounting/providers/annual-declaration-tiruert.provider"
import { formatObjectiveGJ } from "../../../utils/objectives"
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
                  objective: formatObjectiveGJ(progress.target),
                  target_percent: formatNumber(sector.target_percent ?? 0),
                }
              )}
              mainValue={formatEnergyNumber(progress.total_teneur_declared)}
              mainText={t("GJ")}
              baseQuantity={sector.teneur_declared_mj}
              targetQuantity={sector.target_mj ?? 0}
              declaredQuantity={sector.pending_teneur_mj}
              badge={
                <CardProgress.DefaultBadge
                  targetQuantity={progress.target}
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
