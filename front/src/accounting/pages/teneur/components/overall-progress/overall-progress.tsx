import { MainObjective } from "../../types"
import { CardProgress } from "../card-progress"
import { ObjectiveSection } from "../objective-section"
import { Trans, useTranslation } from "react-i18next"
import { RecapData } from "../recap-data"
import { floorNumber, formatNumber } from "common/utils/formatters"
import useEntity from "common/hooks/entity"
import { downloadMacFossilFuel } from "../../api"

type OverallProgressProps = {
  objective?: MainObjective
}

export const OverallProgress = ({ objective }: OverallProgressProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  return (
    <ObjectiveSection
      title={t("Avancement global")}
      description={
        <>
          <span>
            <Trans
              i18nKey="Ces objectifs sont calculés sur la base de vos <a>{{mac}}</a> et d’un PCI théorique."
              values={{
                mac: "mises à consommation 2023",
              }}
              components={{
                strong: <strong />,
                a: (
                  <a
                    className="fr-link--download fr-link"
                    style={{
                      backgroundImage:
                        "var(--underline-img), var(--underline-img)",
                    }}
                    download="true"
                    href="#"
                    onClick={(e) => {
                      e.preventDefault()
                      downloadMacFossilFuel(entity.id)
                    }}
                    target="_blank"
                    rel="noopener noreferrer"
                  />
                ),
              }}
            />
          </span>
          <br />
          <span>
            <Trans
              i18nKey="Base calculée : {{energy_basis}} GJ"
              values={{
                energy_basis: formatNumber(objective?.energy_basis ?? 0, {
                  fractionDigits: 0,
                }),
              }}
            />
          </span>
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
