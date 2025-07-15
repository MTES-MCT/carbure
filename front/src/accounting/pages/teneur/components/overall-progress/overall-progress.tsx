import { MainObjective } from "../../types"
import { CardProgress } from "../card-progress"
import { ObjectiveSection } from "../objective-section"
import { Trans, useTranslation } from "react-i18next"
import { RecapData } from "../recap-data"
import { floorNumber, formatNumber } from "common/utils/formatters"
import useEntity from "common/hooks/entity"
import { downloadMacFossilFuel } from "../../api"
import { Download } from "common/components/download"

type OverallProgressProps = {
  objective?: MainObjective
}

export const OverallProgress = ({ objective }: OverallProgressProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { isAdmin } = entity
  const isAdminOrExternal = isAdmin || entity.isExternal
  return (
    <ObjectiveSection
      title={t("Avancement global")}
      description={
        <>
          {!isAdminOrExternal && (
            <>
              <Trans
                i18nKey="Ces objectifs sont calculés sur la base de vos <a></a> et d’un PCI théorique."
                components={{
                  a: (
                    <Download
                      label={t("mises à consommation") + " 2023"}
                      linkProps={{
                        href: downloadMacFossilFuel(entity.id),
                      }}
                    />
                  ),
                }}
              />
              <br />
              <br />
            </>
          )}

          <Trans
            i18nKey="Base calculée : {{energy_basis}} GJ"
            values={{
              energy_basis: formatNumber(objective?.energy_basis ?? 0, {
                fractionDigits: 0,
              }),
            }}
          />
        </>
      }
    >
      {objective && (
        <CardProgress
          title={t("Total annuel à la date du {{date}}", {
            date: "15/03/2025",
          })}
          description={t(
            "Objectif {{date}}: {{objective}} tCO2 évitées ({{target_percent}}% du total)",
            {
              date: "2025",
              objective: formatNumber(objective.target, {
                fractionDigits: 0,
                mode: "ceil",
              }),
              target_percent: formatNumber(objective.target_percent, {
                fractionDigits: 2,
                appendZeros: false,
              }),
            }
          )}
          mainValue={formatNumber(
            objective.teneur_declared + objective.teneur_declared_month,
            {
              fractionDigits: 0,
            }
          )}
          mainText={t("tCO2 évitées")}
          baseQuantity={floorNumber(objective.teneur_declared, 0)}
          targetQuantity={floorNumber(objective.target, 0)}
          declaredQuantity={floorNumber(objective.teneur_declared_month, 0)}
          badge={
            <CardProgress.DefaultBadge
              targetQuantity={objective.target}
              declaredQuantity={
                objective.teneur_declared + objective.teneur_declared_month
              }
            />
          }
          penalty={objective.penalty}
        >
          <ul>
            <li>
              <RecapData.TeneurDeclaredMonth
                value={t("{{value}} tCO2 évitées", {
                  value: formatNumber(objective.teneur_declared_month, {
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
        </CardProgress>
      )}
    </ObjectiveSection>
  )
}
