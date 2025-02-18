import { Text } from "common/components/text"
import css from "./dialog-section.module.css"

interface DialogSectionProps {
  label: string
  children: React.ReactNode
}

export const DialogSection = ({ label, children }: DialogSectionProps) => {
  return (
    <div className={css["dialog-section"]}>
      {label && (
        <Text fontWeight="bold" className={css["dialog-section__title"]}>
          {label}
        </Text>
      )}
      <div>{children}</div>
    </div>
  )
}
