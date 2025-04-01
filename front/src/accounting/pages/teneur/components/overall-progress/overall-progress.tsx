import { BaseObjective } from "../../types"
import { CardProgress } from "../card-progress"
import { ObjectiveSection } from "../objective-section"
import { useTranslation } from "react-i18next"
import { RecapData } from "../recap-data"
import { ceilNumber, formatNumber } from "common/utils/formatters"

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
              objective: formatNumber(objective.target, {
                fractionDigits: 0,
                mode: "ceil",
              }),
            }
          )}
          mainValue={ceilNumber(objective.teneur_declared, 0)}
          mainText={t("tCO2 évitées")}
          baseQuantity={ceilNumber(objective.teneur_declared, 0)}
          targetQuantity={ceilNumber(objective.target, 0)}
          declaredQuantity={ceilNumber(objective.teneur_declared_month, 0)}
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
                value={t("{{value}} tCO2 évitées", {
                  value: formatNumber(objective.teneur_declared_month, {
                    fractionDigits: 0,
                    mode: "ceil",
                  }),
                })}
              />
            </li>
            <li>
              <RecapData.QuantityAvailable
                value={t("{{value}} tCO2 évitées", {
                  value: formatNumber(objective.quantity_available, {
                    fractionDigits: 0,
                  }),
                })}
              />
            </li>
          </ul>
        </CardProgress>
      )}
    </ObjectiveSection>
  )
}
