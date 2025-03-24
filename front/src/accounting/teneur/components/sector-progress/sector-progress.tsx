import { useTranslation } from "react-i18next"
import { formatSector } from "accounting/utils/formatters"
import { CardProgress } from "../card-progress"
import { ObjectiveSection } from "../objective-section"
import { RecapData } from "../recap-data"
import { SectorObjective } from "accounting/teneur/types"
import { CardGrid } from "../card-grid"
import { formatEnergy } from "accounting/teneur/utils/formatters"
import { ExtendedUnit } from "common/types"
import { formatNumber } from "common/utils/formatters"

type SectorProgressProps = {
  sectors?: SectorObjective[]
}

export const SectorProgress = ({ sectors }: SectorProgressProps) => {
  const { t } = useTranslation()

  return (
    <ObjectiveSection
      title={t("Avancement par filière")}
      description={t("Retrouvez ici votre suivi d'objectif par filière.")}
    >
      <CardGrid>
        {sectors?.map((sector) => (
          <CardProgress
            key={sector.code}
            title={t(formatSector(sector.code))}
            description={t("Objectif en GJ en {{date}}: {{objective}}", {
              date: "2025",
              objective: formatNumber(sector.target),
            })}
            mainValue={sector.teneur_declared}
            mainText={t("GJ")}
            baseQuantity={sector.teneur_declared}
            targetQuantity={sector.target}
            declaredQuantity={sector.teneur_declared_month}
            badge={
              <CardProgress.DefaultBadge
                targetQuantity={sector.target}
                declaredQuantity={
                  sector.teneur_declared + sector.teneur_declared_month
                }
              />
            }
          >
            <ul>
              <li>
                <RecapData.TeneurDeclaredMonth
                  value={formatEnergy(sector.teneur_declared_month, {
                    unit: ExtendedUnit.GJ,
                  })}
                />
              </li>
              <li>
                <RecapData.QuantityAvailable
                  value={formatEnergy(sector.quantity_available, {
                    unit: ExtendedUnit.GJ,
                  })}
                />
              </li>
            </ul>
          </CardProgress>
        ))}
      </CardGrid>
    </ObjectiveSection>
  )
}
