import { useTranslation } from "react-i18next"
import { CardProgress } from "../card-progress"
import { ObjectiveSection } from "../objective-section"
import { RecapData } from "../recap-data"
import { UnconstrainedCategoryObjective } from "../../types"
import { CardGrid } from "../card-grid"
import { formatEnergy } from "../../utils/formatters"
import { ExtendedUnit } from "common/types"

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
                  value={formatEnergy(category.teneur_declared, {
                    unit: ExtendedUnit.GJ,
                  })}
                />
              </li>
              <li>
                <RecapData.TeneurDeclaredMonth
                  value={formatEnergy(category.teneur_declared_month, {
                    unit: ExtendedUnit.GJ,
                  })}
                />
              </li>
              <li>
                <RecapData.QuantityAvailable
                  value={formatEnergy(category.quantity_available, {
                    unit: ExtendedUnit.GJ,
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
