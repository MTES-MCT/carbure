import { useTranslation } from "react-i18next"
import { ObjectiveSection } from "../objective-section"
import { CategoryObjective, TargetType } from "../../../types"
import { CardGrid } from "../../card-grid"
import { CategoryObjectiveProgressCard } from "../category-objective-progress-card"

type ObjectivizedCategoriesProgressProps = {
  categories?: CategoryObjective[]
  onCategoryClick: (category: CategoryObjective, targetType: TargetType) => void
  readOnly: boolean
}

export const ObjectivizedCategoriesProgress = ({
  categories,
  onCategoryClick,
  readOnly,
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
          <CategoryObjectiveProgressCard
            key={category.code}
            category={category}
            readOnly={readOnly}
            onCategoryClick={onCategoryClick}
          />
        ))}
      </CardGrid>
    </ObjectiveSection>
  )
}
