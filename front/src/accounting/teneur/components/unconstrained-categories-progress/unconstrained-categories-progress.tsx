import { useTranslation } from "react-i18next"
import { CardProgress } from "../card-progress"
import { ObjectiveSection } from "../objective-section"
import { RecapData } from "../recap-data"
import { UnconstrainedCategoryObjective } from "accounting/teneur/types"
import { CardGrid } from "../card-grid"

type UnconstrainedCategoriesProgressProps = {
  categories?: UnconstrainedCategoryObjective[]
}

export const UnconstrainedCategoriesProgress = ({
  categories,
}: UnconstrainedCategoriesProgressProps) => {
  const { t } = useTranslation()

  return (
    <ObjectiveSection
      title={t("Catégories ni objectivées ni plafonnées")}
      size="small"
    >
      <CardGrid>
        {categories?.map((category) => (
          <CardProgress key={category.code} title={category.code}>
            <ul>
              <li>
                <RecapData.TeneurDeclared
                  value={category.teneur_declared}
                  unit="GJ"
                />
              </li>
              <li>
                <RecapData.TeneurDeclaredMonth
                  value={category.teneur_declared_month}
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
