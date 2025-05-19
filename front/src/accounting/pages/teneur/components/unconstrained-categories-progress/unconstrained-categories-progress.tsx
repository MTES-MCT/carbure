import { useTranslation } from "react-i18next"
import { CardProgress } from "../card-progress"
import { ObjectiveSection } from "../objective-section"
import { RecapData } from "../recap-data"
import { UnconstrainedCategoryObjective } from "../../types"
import { CardGrid } from "../card-grid"
import { ExtendedUnit } from "common/types"
import { floorNumber, formatUnit } from "common/utils/formatters"
import { useFormatters } from "accounting/hooks/formatters"

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
  return (
    <ObjectiveSection title={t("Autres catégories")} size="small">
      <CardGrid>
        {categories?.map((category) => (
          <CardProgress
            key={category.code}
            title={formatCategory(category.code)}
            onClick={readOnly ? undefined : () => onCategoryClick(category)}
            mainValue={floorNumber(
              category.teneur_declared + category.teneur_declared_month,
              0
            )}
            mainText={t("GJ")}
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
