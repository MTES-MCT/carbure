import { ReactNode, useState } from "react"
import css from "./editable-card.module.css"
import cl from "clsx"
import { Button } from "common/components/button2"
import { Title } from "common/components/title"
import { Text } from "common/components/text"
import { Divider } from "common/components/scaffold"
import { useTranslation } from "react-i18next"
interface EditableCardProps {
  title: string
  description?: string

  /**
   * Children can be a function that receives the editing state and a function to set it.
   * It can also be a ReactNode.
   */
  children:
    | React.ReactNode
    | ((props: {
        isEditing: boolean
        setIsEditing: (editing: boolean) => void
      }) => ReactNode)

  /**
   * Actions to display in the header.
   * If not provided, the default actions (Edit/Cancel)will be displayed.
   * If the value is null, no actions will be displayed.
   */
  headerActions?: ReactNode
  onEdit?: () => void
  onCancel?: () => void
  onSave?: Promise<unknown>
  defaultIsEditing?: boolean
  className?: string
}

export const EditableCard = ({
  title,
  description,
  children,
  headerActions,
  onEdit,
  onSave,
  onCancel,
  defaultIsEditing,
  className,
}: EditableCardProps) => {
  const { t } = useTranslation()
  const [isEditing, setIsEditing] = useState(defaultIsEditing ?? false)

  const handleEdit = () => {
    setIsEditing(true)
    onEdit?.()
  }

  const handleCancel = () => {
    setIsEditing(false)
    onCancel?.()
  }

  return (
    <div className={cl(css["editable-card"], className)}>
      <div className={css["editable-card__header"]}>
        <div>
          <Title className={css["editable-card__title"]} is="p" as="h6">
            {title}
          </Title>
          <Text className={css["editable-card__description"]} size="sm">
            {description}
          </Text>
        </div>

        {headerActions}

        {headerActions === undefined ? (
          <>
            {!isEditing && (
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
            {isEditing && (
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
        {typeof children === "function"
          ? children({ isEditing, setIsEditing })
          : children}
      </div>
    </div>
  )
}
