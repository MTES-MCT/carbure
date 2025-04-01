import { useTranslation } from "react-i18next"
import { CardProgress } from "../card-progress"
import { ObjectiveSection } from "../objective-section"
import { RecapData } from "../recap-data"
import { CategoryObjective, TargetType } from "../../types"
import Badge from "@codegouvfr/react-dsfr/Badge"
import { CardGrid } from "../card-grid"
import { computeObjectiveEnergy, formatEnergy } from "../../utils/formatters"
import { ExtendedUnit } from "common/types"
import { floorNumber } from "common/utils/formatters"

type CappedCategoriesProgressProps = {
  categories?: CategoryObjective[]
  onCategoryClick: (category: CategoryObjective, targetType: TargetType) => void
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
            baseQuantity={floorNumber(category.teneur_declared, 0)}
            targetQuantity={floorNumber(category.target, 0)}
            declaredQuantity={floorNumber(category.teneur_declared_month, 0)}
            badge={
              category.teneur_declared + category.teneur_declared_month >=
              category.target ? (
                <Badge severity="error" small>
                  {t("Plafond atteint")}
                </Badge>
              ) : null
            }
            onClick={() => onCategoryClick(category, TargetType.CAP)}
          >
            <ul>
              <li>
                <RecapData.TeneurDeclaredMonth
                  value={formatEnergy(category.teneur_declared_month, {
                    unit: ExtendedUnit.GJ,
                    fractionDigits: 0,
                  })}
                />
              </li>
              <li>
                <RecapData.RemainingQuantityBeforeLimit
                  value={formatEnergy(computeObjectiveEnergy(category), {
                    unit: ExtendedUnit.GJ,
                    fractionDigits: 0,
                  })}
                />
              </li>
              <li>
                <RecapData.QuantityAvailable
                  value={formatEnergy(category.quantity_available, {
                    unit: ExtendedUnit.GJ,
                    fractionDigits: 0,
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
