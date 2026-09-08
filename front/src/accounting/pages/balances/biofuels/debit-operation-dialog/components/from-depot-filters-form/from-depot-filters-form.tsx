import { AdvancedFiltersBalanceCard } from "accounting/components/advanced-filters/advanced-filters"
import { AdvancedFiltersFormProps } from "accounting/components/advanced-filters/advanced-filters.types"
import { showNextStepAdvancedFilters } from "accounting/components/advanced-filters/advanced-filters.utils"
import {
  FromDepotForm,
  FromDepotFormProps,
} from "accounting/components/from-depot-form"
import { Balance } from "accounting/types"
import { Box } from "common/components/scaffold"
import { Step } from "common/components/stepper"
import i18next from "i18next"
import { ReactNode } from "react"

export type FromDepotFiltersFormProps = FromDepotFormProps &
  AdvancedFiltersFormProps

export const FromDepotFiltersForm = ({
  balance,
  children,
}: {
  balance: Balance
  // Extra field(s) displayed above the depot field (ex: devaluation type)
  children?: ReactNode
}) => {
  return (
    <>
      <Box>
        {children}
        <FromDepotForm />
      </Box>
      <AdvancedFiltersBalanceCard initialBalance={balance} />
    </>
  )
}

export const fromDepotFiltersStepKey = "from-depot-filters"
type FromDepotFiltersStepKey = typeof fromDepotFiltersStepKey

export const fromDepotFiltersStep: (
  values: FromDepotFiltersFormProps,
  overrides?: Partial<Step<FromDepotFiltersStepKey>>
) => Step<FromDepotFiltersStepKey> = (values, overrides) => {
  return {
    key: fromDepotFiltersStepKey,
    title: i18next.t("Dépôt d'expédition et filtres"),
    allowNextStep: showNextStepAdvancedFilters(values),
    ...overrides,
  }
}

export { FromDepotSummary as FromDepotFiltersSummary } from "accounting/components/from-depot-form"
