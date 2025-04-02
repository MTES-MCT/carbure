import { useTranslation } from "react-i18next"
import { CardProgress } from "../card-progress"
import { ObjectiveSection } from "../objective-section"
import { RecapData } from "../recap-data"
import { CategoryObjective, TargetType } from "../../types"
import Badge from "@codegouvfr/react-dsfr/Badge"
import { CardGrid } from "../card-grid"
import { computeObjectiveEnergy } from "../../utils/formatters"
import { ExtendedUnit } from "common/types"
import { floorNumber, formatUnit } from "common/utils/formatters"

type CappedCategoriesProgressProps = {
  categories?: CategoryObjective[]
  onCategoryClick: (category: CategoryObjective, targetType: TargetType) => void
}

export const CappedCategoriesProgress = ({
  categories,
  onCategoryClick,
}: CappedCategoriesProgressProps) => {
  const { t } = useTranslation()

  return (
    <ObjectiveSection
      title={t("Catégories plafonnées")}
      description={t("Catégories dans lesquelles un plafond est fixé.")}
      size="small"
    >
      <CardGrid>
        {categories?.map((category) => (
          <CardProgress
            key={category.code}
            title={category.code}
            baseQuantity={floorNumber(category.teneur_declared, 0)}
            targetQuantity={floorNumber(category.target, 0)}
            declaredQuantity={floorNumber(category.teneur_declared_month, 0)}
            badge={
              category.teneur_declared + category.teneur_declared_month >=
              category.target ? (
                <Badge severity="error" small>
                  {t("Plafond atteint")}
                </Badge>
              ) : null
            }
            onClick={() => onCategoryClick(category, TargetType.CAP)}
          >
            <ul>
              <li>
                <RecapData.TeneurDeclaredMonth
                  value={formatUnit(
                    category.teneur_declared_month,
                    ExtendedUnit.GJ,
                    {
                      fractionDigits: 0,
                    }
                  )}
                />
              </li>
              <li>
                <RecapData.RemainingQuantityBeforeLimit
                  value={formatUnit(
                    computeObjectiveEnergy(category),
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
                    category.quantity_available,
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
