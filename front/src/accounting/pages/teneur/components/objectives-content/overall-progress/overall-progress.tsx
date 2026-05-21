import { MainObjective } from "../../../types"
import { CardProgress } from "../../card-progress"
import { ObjectiveSection } from "../objective-section"
import { Trans, useTranslation } from "react-i18next"
import { RecapData } from "../../recap-data"
import { floorNumber, formatDate, formatNumber } from "common/utils/formatters"
import { useAnnualDeclarationTiruert } from "accounting/providers/annual-declaration-tiruert.provider"

type OverallProgressProps = {
  objective?: MainObjective
}

export const OverallProgress = ({ objective }: OverallProgressProps) => {
  const { t } = useTranslation()
  const { selectedYear, isDeclarationInCurrentPeriod } =
    useAnnualDeclarationTiruert()

  // If the declaration is in the current period, the total annual date is the current date
  // If the declaration is not in the current period, the total annual date is the end of the previous year
  const totalAnnualDate = isDeclarationInCurrentPeriod
    ? new Date()
    : new Date(selectedYear, 2, 31)

  return (
    <ObjectiveSection
      title={t("Avancement global")}
      description={
        <Trans
          i18nKey="Base calculée : {{energy_basis}} GJ"
          values={{
            energy_basis: formatNumber(objective?.energy_basis ?? 0, {
              fractionDigits: 0,
            }),
          }}
        />
      }
    >
      {objective && (
        <CardProgress
          title={t("Total annuel à la date du {{date}}", {
            date: formatDate(totalAnnualDate, "dd/MM/yyyy"),
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
          baseQuantity={floorNumber(objective.teneur_declared, 0)}
          targetQuantity={floorNumber(objective.target, 0)}
          declaredQuantity={floorNumber(objective.pending_teneur, 0)}
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
            <ul>
              <li>
                <RecapData.TeneurDeclaredMonth
                  value={t("{{value}} tCO2 évitées", {
                    value: formatNumber(objective.pending_teneur, {
                      fractionDigits: 0,
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
          )}
        </CardProgress>
      )}
    </ObjectiveSection>
  )
}
