import { useTranslation } from "react-i18next"
import { ObjectiveSection } from "../objective-section"
import { CategoryObjective, TargetType } from "../../../types"
import { CardGrid } from "../../card-grid"
import { CategoryObjectiveProgressCard } from "../category-objective-progress-card"

type ConstrainedCategoriesVariant = "capped" | "objectivized"

type ConstrainedCategoriesProgressProps = {
  variant: ConstrainedCategoriesVariant
  categories?: CategoryObjective[]
  onCategoryClick: (category: CategoryObjective, targetType: TargetType) => void
  readOnly: boolean
}

export const ConstrainedCategoriesProgress = ({
  variant,
  categories,
  onCategoryClick,
  readOnly,
}: ConstrainedCategoriesProgressProps) => {
  const { t } = useTranslation()
  const isCapped = variant === "capped"

  return (
    <ObjectiveSection
      title={
        isCapped ? t("Catégories plafonnées") : t("Catégories objectivées")
      }
      description={
        isCapped
          ? t("Catégories dans lesquelles un plafond est fixé.")
          : t("Catégories pour lesquelles un objectif minimal est requis.")
      }
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
