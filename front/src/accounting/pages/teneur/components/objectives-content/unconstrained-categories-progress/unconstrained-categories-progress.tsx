import { useTranslation } from "react-i18next"
import { CardProgress } from "../../card-progress"
import { ObjectiveSection } from "../objective-section"
import { UnconstrainedCategoryObjective } from "../../../types"
import { CardGrid } from "../../card-grid"
import { useFormatters } from "accounting/hooks/formatters"
import { useAnnualDeclarationTiruert } from "accounting/providers/annual-declaration-tiruert.provider"
import { ObjectiveProgressRecap } from "../objective-progress-recap"
import { formatAccountingNumber } from "accounting/utils/formatters"

type UnconstrainedCategoriesProgressProps = {
  categories?: UnconstrainedCategoryObjective[]
  onCategoryClick: (category: UnconstrainedCategoryObjective) => void
  readOnly: boolean
}

export const UnconstrainedCategoriesProgress = ({
  categories,
  onCategoryClick,
  readOnly,
}: UnconstrainedCategoriesProgressProps) => {
  const { t } = useTranslation()
  const { formatCategory } = useFormatters()
  const { isDeclarationInCurrentPeriod } = useAnnualDeclarationTiruert()

  return (
    <ObjectiveSection title={t("Autres catégories")} size="small">
      <CardGrid>
        {categories?.map((category) => (
          <CardProgress
            key={category.code}
            title={formatCategory(category.code)}
            onClick={
              readOnly || !isDeclarationInCurrentPeriod
                ? undefined
                : () => onCategoryClick(category)
            }
            mainValue={formatAccountingNumber(
              category.progress.total_teneur_declared
            )}
            mainText={t("GJ")}
          >
            {isDeclarationInCurrentPeriod && (
              <ObjectiveProgressRecap objective={category} />
            )}
          </CardProgress>
        ))}
      </CardGrid>
    </ObjectiveSection>
  )
}
