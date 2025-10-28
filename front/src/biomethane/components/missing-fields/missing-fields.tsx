import { Notice } from "common/components/notice"
import { useMissingFieldsMessages } from "./missing-fields.hooks"
import { FormManager } from "common/components/form2"
import { useLocation, useNavigate } from "react-router-dom"
import { useEffect } from "react"

export interface MissingFieldsProps<FormType extends object | undefined> {
  form: FormManager<FormType>
}

export const MissingFields = <FormType extends object | undefined>({
  form,
}: MissingFieldsProps<FormType>) => {
  const { errorMessage, digestateCount, energyCount, showMissingFields } =
    useMissingFieldsMessages(form)
  const location = useLocation()
  const navigate = useNavigate()

  // Clear the hash when the missing fields are shown
  useEffect(() => {
    if (location.hash.includes("missing-fields")) {
      showMissingFields()
      navigate({
        hash: "",
      })
    }
  }, [location.hash])

  if (digestateCount === 0 && energyCount === 0) return null
  return (
    <Notice variant="alert" icon="fr-icon-error-line">
      <div>{errorMessage}</div>
    </Notice>
  )
}
