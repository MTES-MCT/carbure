import { Button, ButtonProps } from "common/components/button2"
import { Text } from "common/components/text"
import { Title } from "common/components/title"
import { ReactNode } from "react"
import css from "./empty-state.module.css"

export type EmptyStateProps = {
  title: ReactNode
  description: ReactNode
  buttonProps?: ButtonProps
}

export const EmptyState = ({
  title,
  description,
  buttonProps,
}: EmptyStateProps) => {
  return (
    <div className={css.root}>
      <div className={css.content}>
        <Title is="h1" as="h5">
          {title}
        </Title>
        <Text size="lg">{description}</Text>
        {buttonProps && <Button size="large" {...buttonProps} />}
      </div>
    </div>
  )
}
