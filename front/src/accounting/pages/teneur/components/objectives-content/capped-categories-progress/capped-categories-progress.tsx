import { useTranslation } from "react-i18next"
import { ObjectiveSection } from "../objective-section"
import { CategoryObjective, TargetType } from "../../../types"
import { CardGrid } from "../../card-grid"
import { CategoryObjectiveProgressCard } from "../category-objective-progress-card"

type CappedCategoriesProgressProps = {
  categories?: CategoryObjective[]
  onCategoryClick: (category: CategoryObjective, targetType: TargetType) => void
  readOnly: boolean
}

export const CappedCategoriesProgress = ({
  categories,
  onCategoryClick,
  readOnly,
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
