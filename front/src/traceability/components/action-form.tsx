import { useEffect } from "react"

import { Fieldset, Form, useForm } from "common/components/form2"
import { Grid } from "common/components/scaffold"
import useEntity from "common/hooks/entity"

import { Action } from "traceability/types"
import {
  ActionField,
  ActionFieldOptions,
  useActionFields,
} from "traceability/hooks/use-action-fields"

export type ActionFormProps = {
  action?: Action
  fields?: ActionField[]
  readOnly?: boolean
}

export const ActionForm = ({
  action,
  fields,
  readOnly = true,
}: ActionFormProps) => {
  const entity = useEntity()
  const actionFields = useActionFields()
  const form = useForm<Partial<Action>>(action ?? {})
  const { setValue } = form

  useEffect(() => {
    if (action) {
      setValue(action)
    }
  }, [action, setValue])

  const defaultFields = Object.values(actionFields) as ActionField[]
  const fieldOptions: ActionFieldOptions = { ...form, readOnly }
  const visibleFields = (fields ?? defaultFields).filter(
    (field) => field.condition?.(entity) ?? true
  )

  const groupedFields = visibleFields.reduce<Record<string, ActionField[]>>(
    (groups, field) => {
      const fieldset = field.fieldset ?? ""
      groups[fieldset] ??= []
      groups[fieldset].push(field)
      return groups
    },
    {}
  )

  return (
    <Form form={form}>
      {Object.entries(groupedFields).map(([fieldset, fieldsetFields]) => (
        <Fieldset key={fieldset || "default"} label={fieldset || undefined}>
          <Grid cols={2} gap="lg">
            {fieldsetFields.map((field) => (
              <div key={String(field.key)}>{field.field(fieldOptions)}</div>
            ))}
          </Grid>
        </Fieldset>
      ))}
    </Form>
  )
}

export default ActionForm
