import { Text } from "common/components/text"
import css from "./dialog-section.module.css"

interface DialogSectionProps {
  label: string
  children: React.ReactNode
}

/**
 * A box with a label and a content (used in dialogs)
 */
export const DialogSection = ({ label, children }: DialogSectionProps) => {
  return (
    <div className={css["dialog-section"]}>
      {label && (
        <Text fontWeight="bold" className={css["dialog-section__title"]}>
          {label}
        </Text>
      )}
      <div className={css["dialog-section__content"]}>{children}</div>
    </div>
  )
}
