import { Box } from "common/components/scaffold"
import { Text } from "common/components/text"
import { useAdvancedFiltersBalance } from "./advanced-filters.hooks"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"

/**
 * Composant avec value qui est un objet avec les filtres et leurs valeurs sélectionnées, selon le type de filtre
 * filtres :
 * - matiere premiere
 * - période de durabilité
 * - taux de réduction GES
 * - Pays d'origine
 *
 * il faut pouvoir faire un appel http pour chaque filtre pour récupérer les options possibles, avec éventuellement les valeurs des autres filtres
 *
 * Plan :
 * - Utiliser l'endpoint /api/accounting/biofuels/filters pour récupérer les options possibles pour chaque filtre et en faire un hook useGetFilterOptions
 * - Utiliser le hook useGetFilterOptions pour récupérer les options possibles pour chaque filtre
 * - définir les labels pour chaque filtre
 * - Populer les valeurs de la variable value dans les champs
 */

export type AdvancedFiltersBalanceProps = {
  value?: {
    feedstock: string[]
    durabilityPeriod: string[]
    originCountry: string[]
  }
}

export const AdvancedFiltersBalance = (props: AdvancedFiltersBalanceProps) => {
  const { getFilterOptions, state, actions, filterNormalizers, filterLabels } =
    useAdvancedFiltersBalance()
  return (
    <FilterMultiSelect2
      filterLabels={filterLabels}
      getFilterOptions={getFilterOptions}
      selected={state.filters}
      onSelect={actions.setFilters}
      normalizers={filterNormalizers}
    />
  )
}

export const AdvancedFiltersBalanceCard = (
  props: AdvancedFiltersBalanceProps
) => (
  <Box>
    <Text>Filtres avancés</Text>
    <AdvancedFiltersBalance {...props} />
  </Box>
)
