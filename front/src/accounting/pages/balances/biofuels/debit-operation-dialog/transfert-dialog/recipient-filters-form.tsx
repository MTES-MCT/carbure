import { Box } from "common/components/scaffold"
import {
  RecipientForm,
  RecipientFormProps,
} from "accounting/components/recipient-form"
import { AdvancedFiltersFormProps } from "accounting/components/advanced-filters/advanced-filters.types"
import { useFormContext } from "common/components/form2"
import { AdvancedFiltersBalanceCard } from "accounting/components/advanced-filters/advanced-filters"
import { Step } from "common/components/stepper"
import i18next from "i18next"
import { showNextStepAdvancedFilters } from "accounting/components/advanced-filters/advanced-filters.utils"

type RecipientFiltersFormProps = RecipientFormProps & AdvancedFiltersFormProps

export const RecipientFiltersForm = () => {
  const form = useFormContext<RecipientFiltersFormProps>()
  return (
    <>
      <Box>
        <RecipientForm />
      </Box>
      {form.value.balance && <AdvancedFiltersBalanceCard />}
    </>
  )
}

export const recipientFiltersStepKey = "recipient_filters"
type RecipientFiltersStepKey = typeof recipientFiltersStepKey

export const recipientFiltersStep: (
  values: RecipientFiltersFormProps
) => Step<RecipientFiltersStepKey> = (values) => {
  return {
    key: recipientFiltersStepKey,
    title: i18next.t("Destinataire et filtres"),
    allowNextStep: showNextStepAdvancedFilters(values),
  }
}

export { RecipientSummary as RecipientFiltersSummary } from "accounting/components/recipient-form"
