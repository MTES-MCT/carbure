import { useTranslation } from "react-i18next"
import { formatSector } from "accounting/utils/formatters"
import { CardProgress } from "../card-progress"
import { ObjectiveSection } from "../objective-section"
import { RecapData } from "../recap-data"
import { SectorObjective } from "../../types"
import { CardGrid } from "../card-grid"
import { ExtendedUnit } from "common/types"
import { floorNumber, formatNumber, formatUnit } from "common/utils/formatters"

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
            title={formatSector(sector.code)}
            description={t(
              "Objectif en GJ en {{date}}: {{objective}} ({{target_percent}}% du total)",
              {
                date: "2025",
                objective: formatUnit(sector.target, ExtendedUnit.GJ, {
                  fractionDigits: 0,
                }),
                target_percent: formatNumber(sector.target_percent),
              }
            )}
            mainValue={floorNumber(
              sector.teneur_declared + sector.teneur_declared_month,
              0
            )}
            mainText={t("GJ")}
            baseQuantity={floorNumber(sector.teneur_declared, 0)}
            targetQuantity={floorNumber(sector.target, 0)}
            declaredQuantity={floorNumber(sector.teneur_declared_month, 0)}
            badge={
              <CardProgress.DefaultBadge
                targetQuantity={sector.target}
                declaredQuantity={
                  sector.teneur_declared + sector.teneur_declared_month
                }
              />
            }
            penalty={sector.penalty}
          >
            <ul>
              <li>
                <RecapData.TeneurDeclaredMonth
                  value={formatUnit(
                    sector.teneur_declared_month,
                    ExtendedUnit.GJ,
                    {
                      fractionDigits: 0,
                    }
                  )}
                />
              </li>
              <li>
                <RecapData.QuantityAvailable
                  value={formatUnit(
                    sector.quantity_available,
                    ExtendedUnit.GJ,
                    {
                      fractionDigits: 0,
                    }
                  )}
                />
              </li>
            </ul>
          </CardProgress>
        ))}
      </CardGrid>
    </ObjectiveSection>
  )
}
