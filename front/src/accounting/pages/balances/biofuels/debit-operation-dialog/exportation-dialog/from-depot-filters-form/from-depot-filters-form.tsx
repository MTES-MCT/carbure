import { AdvancedFiltersBalanceCard } from "accounting/components/advanced-filters/advanced-filters"
import { AdvancedFiltersFormProps } from "accounting/components/advanced-filters/advanced-filters.types"
import { showNextStepAdvancedFilters } from "accounting/components/advanced-filters/advanced-filters.utils"
import {
  FromDepotForm,
  FromDepotFormProps,
} from "accounting/components/from-depot-form"
import { useFormContext } from "common/components/form2"
import { Box } from "common/components/scaffold"
import { Step } from "common/components/stepper"
import i18next from "i18next"

type FromDepotFiltersFormProps = FromDepotFormProps & AdvancedFiltersFormProps

export const FromDepotFiltersForm = () => {
  const form = useFormContext<FromDepotFiltersFormProps>()

  return (
    <>
      <Box>
        <FromDepotForm />
      </Box>
      {form.value.balance && <AdvancedFiltersBalanceCard />}
    </>
  )
}

export const fromDepotFiltersStepKey = "from-depot-filters"
type FromDepotFiltersStepKey = typeof fromDepotFiltersStepKey

export const fromDepotFiltersStep: (
  values: FromDepotFiltersFormProps
) => Step<FromDepotFiltersStepKey> = (values) => {
  return {
    key: fromDepotFiltersStepKey,
    title: i18next.t("Dépôt d'expédition et filtres"),
    allowNextStep: showNextStepAdvancedFilters(values),
  }
}

export { FromDepotSummary as FromDepotFiltersSummary } from "accounting/components/from-depot-form"
