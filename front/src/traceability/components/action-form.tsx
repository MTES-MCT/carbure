import { useEffect } from "react"

import { Form, useForm } from "common/components/form2"
import { Grid } from "common/components/scaffold"
import useEntity from "common/hooks/entity"

import { Action } from "traceability/types"
import { ActionField } from "traceability/hooks/use-action-fields"

export type ActionFormProps = {
  action?: Action
  readOnly?: boolean
  fields: ActionField[]
}

export const ActionForm = ({
  action,
  fields,
  readOnly = true,
}: ActionFormProps) => {
  const entity = useEntity()
  const form = useForm<Partial<Action>>(action ?? {})
  const { setValue } = form

  useEffect(() => {
    if (action) setValue(action)
  }, [action, setValue])

  const visibleFields = fields.filter(
    (field) => field.condition?.(entity) ?? true
  )

  return (
    <Form form={form}>
      <Grid cols={2} gap="lg">
        {visibleFields?.map((field) => (
          <div key={field.key}>
            {field.field({ form, readOnly, label: field.label })}
          </div>
        ))}
      </Grid>
    </Form>
  )
}

export default ActionForm
