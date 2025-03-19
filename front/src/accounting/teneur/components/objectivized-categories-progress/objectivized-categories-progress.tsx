import { useTranslation } from "react-i18next"
import { CardProgress } from "../card-progress"
import { ObjectiveSection } from "../objective-section"
import { RecapData } from "../recap-data"
import { CategoryObjective } from "accounting/teneur/types"
import { CategoryEnum } from "common/types"
import { CardGrid } from "../card-grid"

type ObjectivizedCategoriesProgressProps = {
  categories?: CategoryObjective[]
  onCategoryClick: (category: CategoryEnum) => void
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
            baseQuantity={category.teneur_declared}
            targetQuantity={category.target}
            declaredQuantity={category.teneur_declared_month}
            badge={
              <CardProgress.DefaultBadge
                targetQuantity={category.target}
                declaredQuantity={
                  category.teneur_declared + category.teneur_declared_month
                }
              />
            }
            onClick={() => onCategoryClick(category.code)}
          >
            <ul>
              <li>
                <RecapData.TeneurDeclaredMonth
                  value={category.teneur_declared_month}
                  unit="GJ"
                />
              </li>
              <li>
                <RecapData.RemainingQuantityBeforeObjective
                  value={
                    category.target -
                    category.teneur_declared -
                    category.teneur_declared_month
                  }
                  unit="GJ"
                />
              </li>
              <li>
                <RecapData.QuantityAvailable
                  value={category.quantity_available}
                  unit="GJ"
                />
              </li>
            </ul>
          </CardProgress>
        ))}
      </CardGrid>
    </ObjectiveSection>
  )
}
