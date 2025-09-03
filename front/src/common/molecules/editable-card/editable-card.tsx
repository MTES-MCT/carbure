import { ReactNode } from "react"
import css from "./editable-card.module.css"
import cl from "clsx"
import { Button } from "common/components/button2"
import { Title } from "common/components/title"
import { Text } from "common/components/text"
import { Divider } from "common/components/scaffold"
import { useTranslation } from "react-i18next"
import { EditableCardProvider, useEditableCard } from "./editable-card.provider"
import { Form, FormProps } from "common/components/form2"

interface EditableCardProps {
  title: string
  description?: ReactNode

  /**
   * Children can be a function that receives the editing state and a function to set it.
   * It can also be a ReactNode.
   */
  children: React.ReactNode | ((props: { isEditing: boolean }) => ReactNode)

  /**
   * Actions to display in the header.
   * If not provided, the default actions (Edit/Cancel)will be displayed.
   * If the value is null, no actions will be displayed.
   */
  headerActions?: ReactNode
  defaultIsEditing?: boolean
  isEditing?: boolean
  onEdit?: (isEditing: boolean) => void
  onCancel?: () => void
  className?: string
  readOnly?: boolean
}

// Internal component that uses the context
/**
 * This component is a simple card with a title, description, edit button to toggle the editing state and a content area.
 * The editing state is controlled by the component itself, but it can be overridden by the `isEditing` prop.
 * See more examples in the storybook.
 */
const EditableCardContent = ({
  title,
  description,
  children,
  headerActions,
  className,
  isEditing: controlledIsEditing,
  readOnly,
  onEdit: controlledOnEdit,
  onCancel: controlledOnCancel,
}: EditableCardProps) => {
  const { t } = useTranslation()
  const { isEditing, setIsEditing } = useEditableCard()

  // Use controlled state if provided, otherwise use internal state
  const currentIsEditing =
    controlledIsEditing !== undefined ? controlledIsEditing : isEditing

  const handleEdit = () => {
    if (controlledOnEdit) {
      controlledOnEdit(true)
    } else {
      setIsEditing(true)
    }
  }

  const handleCancel = () => {
    controlledOnCancel?.()
    if (controlledOnEdit) {
      controlledOnEdit(false)
    } else {
      setIsEditing(false)
    }
  }

  return (
    <div className={cl(css["editable-card"], className)}>
      <div className={css["editable-card__header"]}>
        <div>
          <Title className={css["editable-card__title"]} is="p" as="h6">
            {title}
          </Title>
          {description ? (
            <Text className={css["editable-card__description"]} size="sm">
              {description}
            </Text>
          ) : null}
        </div>

        {headerActions}

        {headerActions === undefined && !readOnly ? (
          <>
            {!currentIsEditing && (
              <Button
                onClick={handleEdit}
                asideX
                priority="tertiary no outline"
                iconId="ri-edit-2-line"
                iconPosition="right"
                size="small"
              >
                {t("Modifier")}
              </Button>
            )}
            {currentIsEditing && (
              <Button
                onClick={handleCancel}
                asideX
                priority="tertiary no outline"
                iconId="ri-close-line"
                iconPosition="right"
                size="small"
              >
                {t("Annuler")}
              </Button>
            )}
          </>
        ) : null}
      </div>

      <Divider noMargin />

      <div className={css["editable-card__content"]}>
        {typeof children === "function" ? children({ isEditing }) : children}
      </div>
    </div>
  )
}

/**
 * A wrapper around the Form component that will close the editing state of the EditableCard when the onSubmit prop is triggered on success.
 * @param props - The props of the Form component.
 * @returns The Form component.
 */
const EditableCardForm = <T,>(props: FormProps<T>) => {
  const { isEditing, setIsEditing } = useEditableCard()

  const onSubmit: FormProps<T>["onSubmit"] = async (...args) => {
    await props.onSubmit?.(...args)
    setIsEditing(!isEditing)
  }
  return <Form {...props} onSubmit={onSubmit} />
}

export const EditableCard = ({
  defaultIsEditing,
  ...props
}: EditableCardProps) => {
  return (
    <EditableCardProvider defaultIsEditing={defaultIsEditing}>
      <EditableCardContent {...props} />
    </EditableCardProvider>
  )
}

EditableCard.Form = EditableCardForm
