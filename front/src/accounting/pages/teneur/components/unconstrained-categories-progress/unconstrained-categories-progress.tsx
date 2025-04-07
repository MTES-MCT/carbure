import { useTranslation } from "react-i18next"
import { CardProgress } from "../card-progress"
import { ObjectiveSection } from "../objective-section"
import { RecapData } from "../recap-data"
import { UnconstrainedCategoryObjective } from "../../types"
import { CardGrid } from "../card-grid"
import { ExtendedUnit } from "common/types"
import { formatUnit } from "common/utils/formatters"

type UnconstrainedCategoriesProgressProps = {
  categories?: UnconstrainedCategoryObjective[]
  onCategoryClick: (category: UnconstrainedCategoryObjective) => void
}

export const UnconstrainedCategoriesProgress = ({
  categories,
  onCategoryClick,
}: UnconstrainedCategoriesProgressProps) => {
  const { t } = useTranslation()

  return (
    <ObjectiveSection
      title={t("Catégories ni objectivées ni plafonnées")}
      size="small"
    >
      <CardGrid>
        {categories?.map((category) => (
          <CardProgress
            key={category.code}
            title={category.code}
            onClick={() => onCategoryClick(category)}
          >
            <ul>
              <li>
                <RecapData.TeneurDeclared
                  value={formatUnit(category.teneur_declared, ExtendedUnit.GJ, {
                    fractionDigits: 0,
                  })}
                />
              </li>
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
