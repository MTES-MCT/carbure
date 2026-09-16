import { useEffect } from "react"

import { Form, useForm } from "common/components/form2"

import { Action } from "traceability/types"
import { ActionFieldset } from "traceability/hooks/action-fields"
import { ActionFormFieldset } from "./action-form-fieldset"

export type ActionFormProps = {
  action?: Action
  readOnly?: boolean
  fieldsets: ActionFieldset[]
}

export const ActionForm = ({
  action,
  fieldsets,
  readOnly = true,
}: ActionFormProps) => {
  const form = useForm<Partial<Action>>(action ?? {})
  const { setValue } = form

  useEffect(() => {
    if (action) setValue(action)
  }, [action, setValue])

  return (
    <Form form={form} variant="modal">
      {fieldsets.map((fieldset) => (
        <ActionFormFieldset
          key={fieldset.legend}
          readOnly={readOnly}
          form={form}
          fieldset={fieldset}
        />
      ))}
    </Form>
  )
}

export default ActionForm
