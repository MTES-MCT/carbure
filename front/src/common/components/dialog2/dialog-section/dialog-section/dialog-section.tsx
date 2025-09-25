import { Text } from "common/components/text"
import css from "./dialog-section.module.css"
import clsx from "clsx"

interface DialogSectionProps {
  label: string
  children: React.ReactNode
  gap?: "md" | "lg"
}

/**
 * A box with a label and a content (used in dialogs)
 */
export const DialogSection = ({
  label,
  children,
  gap = "md",
}: DialogSectionProps) => {
  return (
    <div className={css["dialog-section"]}>
      {label && (
        <Text fontWeight="bold" className={css["dialog-section__title"]}>
          {label}
        </Text>
      )}
      <div
        className={clsx(
          css["dialog-section__content"],
          css[`dialog-section__content--gap-${gap}`]
        )}
      >
        {children}
      </div>
    </div>
  )
}
