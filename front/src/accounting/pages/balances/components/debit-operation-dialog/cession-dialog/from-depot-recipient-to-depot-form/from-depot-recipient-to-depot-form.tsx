import {
  FromDepotForm,
  FromDepotFormProps,
  FromDepotSummary,
  showNextStepFromDepotForm,
} from "accounting/components/from-depot-form"
import {
  RecipientToDepotForm,
  RecipientToDepotFormProps,
  RecipientToDepotSummary,
  showNextStepRecipientToDepotForm,
} from "accounting/components/recipient-to-depot-form"
import { Balance } from "accounting/types"
import { Step } from "common/components/stepper"
import i18next from "i18next"

export const FromDepotRecipientToDepotForm = ({
  balance,
}: {
  balance: Balance
}) => {
  return (
    <>
      <RecipientToDepotForm />
      <FromDepotForm balance={balance} />
    </>
  )
}

export const FromDepotRecipientToDepotSummary = ({
  values,
}: {
  values: FromDepotRecipientToDepotFormProps
}) => (
  <>
    <RecipientToDepotSummary values={values} />
    <FromDepotSummary values={values} />
  </>
)

export type FromDepotRecipientToDepotFormProps = RecipientToDepotFormProps &
  FromDepotFormProps

export const fromDepotRecipientToDepotStepKey = "from-depot-recipient-to-depot"
type FromDepotRecipientToDepotStepKey = typeof fromDepotRecipientToDepotStepKey

export const fromDepotRecipientToDepotStep: (
  values: FromDepotRecipientToDepotFormProps
) => Step<FromDepotRecipientToDepotStepKey> = (values) => ({
  key: fromDepotRecipientToDepotStepKey,
  title: i18next.t("Dépôt d'expédition, destinataire et dépôt destinataire"),
  allowNextStep: showNextStepFromDepotRecipientToDepotForm(values),
})

export const showNextStepFromDepotRecipientToDepotForm = (
  values: FromDepotRecipientToDepotFormProps
) =>
  showNextStepRecipientToDepotForm(values) && showNextStepFromDepotForm(values)
