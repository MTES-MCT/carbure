import {
  FromDepotFormProps,
  FromDepotSummary,
  showNextStepFromDepotForm,
} from "accounting/components/from-depot-form"
import {
  RecipientFormProps,
  RecipientSummary,
  showNextStepRecipientForm,
} from "accounting/components/recipient-form"
import {
  ToDepotFormProps,
  ToDepotSummary,
} from "accounting/components/to-depot-form"
import { Step } from "common/components/stepper"
import i18next from "i18next"

export const FromDepotRecipientToDepotSummary = ({
  values,
}: {
  values: FromDepotRecipientToDepotFormProps
}) => (
  <>
    <RecipientSummary values={values} />
    <ToDepotSummary values={values} />
    <FromDepotSummary values={values} />
  </>
)

export type FromDepotRecipientToDepotFormProps = RecipientFormProps &
  ToDepotFormProps &
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
) => showNextStepRecipientForm(values) && showNextStepFromDepotForm(values)
