import { Box } from "common/components/scaffold"
import { useTranslation } from "react-i18next"
import { ObjectiveSection } from "./objective-section"
import { OverallProgress } from "./overall-progress"
import { SectorProgress } from "./sector-progress"
import { CappedCategoriesProgress } from "./capped-categories-progress"
import { ObjectivizedCategoriesProgress } from "./objectivized-categories-progress"
import { UnconstrainedCategoriesProgress } from "./unconstrained-categories-progress"
import type {
  CategoryObjective,
  TargetType,
  UnconstrainedCategoryObjective,
  Objectives,
} from "../../types"

type ObjectivesContentProps = {
  objectivesData: Objectives | undefined
  readOnly: boolean
  onCategoryClick?: (
    objective: CategoryObjective | UnconstrainedCategoryObjective,
    targetType?: TargetType
  ) => void
}

export const ObjectivesContent = ({
  objectivesData,
  readOnly,
  onCategoryClick = () => {},
}: ObjectivesContentProps) => {
  const { t } = useTranslation()

  return (
    <Box gap="lg">
      <OverallProgress objective={objectivesData?.global} />
      <SectorProgress sectors={objectivesData?.sectors} />
      <ObjectiveSection
        title={t("Avancement par catégorie de carburants alternatifs")}
      >
        <CappedCategoriesProgress
          categories={objectivesData?.capped_categories}
          onCategoryClick={onCategoryClick}
          readOnly={readOnly}
        />
        <ObjectivizedCategoriesProgress
          categories={objectivesData?.objectivized_categories}
          onCategoryClick={onCategoryClick}
          readOnly={readOnly}
        />
        <UnconstrainedCategoriesProgress
          categories={objectivesData?.unconstrained_categories}
          onCategoryClick={onCategoryClick}
          readOnly={readOnly}
        />
      </ObjectiveSection>
    </Box>
  )
}
