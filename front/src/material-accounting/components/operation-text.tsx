import { Text } from "common/components/text"
import css from "./operation-text.module.css"
interface OperationTextProps {
  title: string
  description: string
}

export const OperationText = ({ title, description }: OperationTextProps) => {
  return (
    <div>
      <Text className={css["operation-text-title"]}>{title}</Text>
      <Text className={css["operation-text-description"]}>{description}</Text>
    </div>
  )
}
