import { BaseObjective } from "accounting/teneur/types"
import { CardProgress } from "../card-progress"
import { ObjectiveSection } from "../objective-section"
import { useTranslation } from "react-i18next"
import { RecapData } from "../recap-data"

type OverallProgressProps = {
  objective?: BaseObjective
}

export const OverallProgress = ({ objective }: OverallProgressProps) => {
  const { t } = useTranslation()
  return (
    <ObjectiveSection
      title={t("Avancement global")}
      description={t(
        "Ces objectifs sont calculés sur la base de vos mises à la consommation décadaires. Ces mises à la consommation ne sont pas consolidées et sont calculées sur la base d’un PCI théorique."
      )}
    >
      {objective && (
        <CardProgress
          title={t("Total annuel à la date du {{date}}", {
            date: "15/03/2025",
          })}
          description={t(
            "Objectif en tC02 évitées en {{date}}: {{objective}} tC02 évitées",
            {
              date: "2025",
              objective: objective.target,
            }
          )}
          mainValue={objective.teneur_declared}
          mainText={t("tCO2 évitées")}
          baseQuantity={objective.teneur_declared}
          targetQuantity={objective.target}
          declaredQuantity={objective.teneur_declared_month}
          badge={
            <CardProgress.DefaultBadge
              targetQuantity={objective.target}
              declaredQuantity={
                objective.teneur_declared + objective.teneur_declared_month
              }
            />
          }
        >
          <ul>
            <li>
              <RecapData.TeneurDeclaredMonth
                value={objective.teneur_declared_month}
                unit={t("tCO2 évitées")}
              />
            </li>
            <li>
              <RecapData.QuantityAvailable
                value={objective.quantity_available}
                unit={t("tCO2 évitées")}
              />
            </li>
          </ul>
        </CardProgress>
      )}
    </ObjectiveSection>
  )
}
