import { useTranslation } from "react-i18next"
import { CardProgress } from "../card-progress"
import { ObjectiveSection } from "../objective-section"
import { RecapData } from "../recap-data"
import { CategoryObjective, TargetType } from "../../types"
import { CardGrid } from "../card-grid"
import { computeObjectiveEnergy, formatEnergy } from "../../utils/formatters"
import { ExtendedUnit } from "common/types"
import { ceilNumber } from "common/utils/formatters"

type ObjectivizedCategoriesProgressProps = {
  categories?: CategoryObjective[]
  onCategoryClick: (category: CategoryObjective, targetType: TargetType) => void
}

export const ObjectivizedCategoriesProgress = ({
  categories,
  onCategoryClick,
}: ObjectivizedCategoriesProgressProps) => {
  const { t } = useTranslation()

  return (
    <ObjectiveSection
      title={t("Catégories objectivées")}
      description={t(
        "Catégories pour lesquelles un objectif minimal est requis."
      )}
      size="small"
    >
      <CardGrid>
        {categories?.map((category) => (
          <CardProgress
            key={category.code}
            title={category.code}
            baseQuantity={ceilNumber(category.teneur_declared)}
            targetQuantity={ceilNumber(category.target)}
            declaredQuantity={ceilNumber(category.teneur_declared_month)}
            badge={
              <CardProgress.DefaultBadge
                targetQuantity={category.target}
                declaredQuantity={
                  category.teneur_declared + category.teneur_declared_month
                }
              />
            }
            onClick={() => onCategoryClick(category, TargetType.REACH)}
          >
            <ul>
              <li>
                <RecapData.TeneurDeclaredMonth
                  value={formatEnergy(category.teneur_declared_month, {
                    unit: ExtendedUnit.GJ,
                    fractionDigits: 0,
                  })}
                />
              </li>
              <li>
                <RecapData.RemainingQuantityBeforeObjective
                  value={formatEnergy(computeObjectiveEnergy(category), {
                    unit: ExtendedUnit.GJ,
                    fractionDigits: 0,
                    mode: "ceil",
                  })}
                />
              </li>
              <li>
                <RecapData.QuantityAvailable
                  value={formatEnergy(category.quantity_available, {
                    unit: ExtendedUnit.GJ,
                    fractionDigits: 0,
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
