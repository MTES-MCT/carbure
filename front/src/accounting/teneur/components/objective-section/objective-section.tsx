import { Text } from "common/components/text"
import { Title } from "common/components/title"
import css from "./objective-section.module.css"

type ObjectiveSectionProps = {
  title: string
  description?: string
  size?: "small"
  children?: React.ReactNode
}

export const ObjectiveSection = ({
  title,
  description,
  size,
  children,
}: ObjectiveSectionProps) => {
  return (
    <div>
      <Title
        is={size === "small" ? "h2" : "h1"}
        as={size === "small" ? "h6" : "h3"}
      >
        {title}
      </Title>
      {description && (
        <Text className={css["objective-section__text"]}>{description}</Text>
      )}
      <div className={css["objective-section__content"]}>{children}</div>
    </div>
  )
}
