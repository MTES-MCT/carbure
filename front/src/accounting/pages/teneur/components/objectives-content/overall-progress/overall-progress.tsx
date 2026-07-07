import { MainObjective } from "../../../types"
import { CardProgress } from "../../card-progress"
import { ObjectiveSection } from "../objective-section"
import { Trans, useTranslation } from "react-i18next"
import { RecapData } from "../../recap-data"
import { formatNumber } from "common/utils/formatters"
import { useAnnualDeclarationTiruert } from "accounting/providers/annual-declaration-tiruert.provider"

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
            energy_basis: formatNumber(objective?.energy_basis ?? 0, {
              fractionDigits: 0,
            }),
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
