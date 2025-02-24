import { Text } from "common/components/text"
import css from "./operation-text.module.css"
import { ReactNode } from "react"
interface OperationTextProps {
  title: ReactNode
  description: ReactNode
}

export const OperationText = ({ title, description }: OperationTextProps) => {
  return (
    <div>
      <Text className={css["operation-text-title"]}>{title}</Text>
      <Text className={css["operation-text-description"]}>{description}</Text>
    </div>
  )
}
