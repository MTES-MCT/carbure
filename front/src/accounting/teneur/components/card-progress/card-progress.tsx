import { Fragment, ReactNode } from "react"
import { Badge } from "@codegouvfr/react-dsfr/Badge"
import { useTranslation } from "react-i18next"
import css from "./card-progress.module.css"
import { Text } from "common/components/text/text"
import { Title } from "common/components/title/title"
import { ProgressBar } from "../progress-bar"
import cl from "clsx"
import { ArrowRightLine } from "common/components/icon"

export type CardProgressProps = {
  title?: string

  mainValue?: number
  mainText?: string
  description?: string
  children?: ReactNode

  // Target quantity
  targetQuantity: number

  baseQuantity: number

  // Currently declared quantity
  declaredQuantity: number

  // Allow to display custom badge
  badge?: ReactNode

  onClick?: () => void
}
export const CardProgress = ({
  title,
  baseQuantity,
  targetQuantity,
  declaredQuantity,
  mainText,
  mainValue,
  description,
  badge,
  children,
  onClick,
}: CardProgressProps) => {
  const ButtonOrFragment = onClick ? "button" : "div"

  return (
    <ButtonOrFragment className={cl(onClick && css["card-progress-button"])}>
      <div className={css["card-progress"]}>
        <div className={css["card-progress__header"]}>
          {title ? (
            <Text is="span" fontWeight="bold">
              {title}
            </Text>
          ) : null}
          {badge}
        </div>
        <div>
          {mainValue ? (
            <Title is="p" as="h1">
              {mainValue}
              {mainText ? (
                <Title is="span" as="h5">
                  {" "}
                  {mainText}
                </Title>
              ) : null}
            </Title>
          ) : null}
          {description && (
            <div className={css["card-progress__description"]}>
              <Text size="sm">{description}</Text>
            </div>
          )}
        </div>

        <ProgressBar
          targetQuantity={targetQuantity}
          baseQuantity={baseQuantity}
          declaredQuantity={declaredQuantity}
        />
        {children}
        {onClick && (
          <ArrowRightLine
            asideX
            className={css["card-progress__arrow-right"]}
          />
        )}
      </div>
    </ButtonOrFragment>
  )
}

const DefaultBadge = ({
  targetQuantity,
  declaredQuantity,
}: {
  targetQuantity: number
  declaredQuantity: number
}) => {
  const { t } = useTranslation()
  const severity = targetQuantity > declaredQuantity ? "error" : "success"

  return (
    <Badge severity={severity}>
      {targetQuantity > declaredQuantity ? t("Non atteint") : t("Atteint")}
    </Badge>
  )
}

CardProgress.DefaultBadge = DefaultBadge
