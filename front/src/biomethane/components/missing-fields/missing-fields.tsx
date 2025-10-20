import { Notice } from "common/components/notice"
import { useMissingFieldsMessages } from "./missing-fields.hooks"
import { FormManager } from "common/components/form2"

type Page = "digestate" | "energy"

export interface MissingFieldsProps<FormType extends object> {
  form: FormManager<FormType>
  page: Page
}

export const MissingFields = <FormType extends object>({
  form,
}: MissingFieldsProps<FormType>) => {
  const { errorMessage, digestateCount, energyCount } =
    useMissingFieldsMessages(form)

  if (digestateCount === 0 && energyCount === 0) return null
  return (
    <Notice variant="alert" icon="fr-icon-error-line">
      {errorMessage}
    </Notice>
  )
}
