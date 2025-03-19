import { useTranslation } from "react-i18next"
import { CardProgress } from "../card-progress"
import { ObjectiveSection } from "../objective-section"
import { RecapData } from "../recap-data"
import { CategoryObjective } from "accounting/teneur/types"
import Badge from "@codegouvfr/react-dsfr/Badge"
import { CategoryEnum } from "common/types"
import { CardGrid } from "../card-grid"

type CappedCategoriesProgressProps = {
  categories?: CategoryObjective[]
  onCategoryClick: (category: CategoryEnum) => void
}

export const CappedCategoriesProgress = ({
  categories,
  onCategoryClick,
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
          <CardProgress
            key={category.code}
            title={category.code}
            baseQuantity={category.teneur_declared}
            targetQuantity={category.target}
            declaredQuantity={category.teneur_declared_month}
            badge={
              category.teneur_declared + category.teneur_declared_month >=
              category.target ? (
                <Badge severity="error" small>
                  {t("Plafond atteint")}
                </Badge>
              ) : null
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
                <RecapData.RemainingQuantityBeforeLimit
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
