import { Dialog } from "common/components/dialog2"
import { FormManager } from "common/components/form2"
import useEntity from "common/hooks/entity"
import { Fragment } from "react/jsx-runtime"
import { ActionFieldset as ActionFieldsetConfig } from "traceability/hooks/action-fields"
import { Action } from "traceability/types"

type ActionFieldsetProps = {
  readOnly?: boolean
  form: FormManager<Partial<Action>>
  fieldset: ActionFieldsetConfig
}

export const ActionFormFieldset = ({
  readOnly,
  form,
  fieldset,
}: ActionFieldsetProps) => {
  const entity = useEntity()

  const visibleFields = fieldset.fields.filter(
    (field) => field.condition?.(entity) ?? true
  )

  return (
    <Dialog.Section label={fieldset.legend}>
      {visibleFields?.map((field) => (
        <Fragment key={field.key}>
          {field.field({
            form,
            props: { readOnly, label: field.label },
            options: field.options,
          })}
        </Fragment>
      ))}
    </Dialog.Section>
  )
}
