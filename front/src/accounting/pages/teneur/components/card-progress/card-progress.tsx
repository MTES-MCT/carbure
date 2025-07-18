import { ReactNode } from "react"
import { Badge } from "@codegouvfr/react-dsfr/Badge"
import { useTranslation } from "react-i18next"
import css from "./card-progress.module.css"
import { Text } from "common/components/text/text"
import { Title } from "common/components/title/title"
import { ProgressBar } from "../progress-bar"
import cl from "clsx"
import { ArrowRightLine } from "common/components/icon"
import { CONVERSIONS, formatNumber } from "common/utils/formatters"

export type CardProgressProps = {
  title?: string

  mainValue?: ReactNode
  mainText?: ReactNode
  description?: string
  children?: ReactNode

  // Target quantity
  targetQuantity?: number

  baseQuantity?: number

  // Currently declared quantity
  declaredQuantity?: number

  // Allow to display custom badge
  badge?: ReactNode

  penalty?: number

  onClick?: () => void

  className?: string
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
  penalty,
  children,
  onClick,
  className,
}: CardProgressProps) => {
  const ButtonOrFragment = onClick ? "button" : "div"

  return (
    <ButtonOrFragment
      className={cl(onClick && css["card-progress-button"], className)}
      {...(onClick && { onClick })}
    >
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
          {mainValue !== undefined ? (
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <Title is="p" as="h2">
                {mainValue}
                {mainText !== undefined ? (
                  <Title is="span" as="h5">
                    {" "}
                    {mainText}
                  </Title>
                ) : null}
              </Title>
              {!!penalty && (
                <Text size="sm">
                  Sanction :{" "}
                  {formatNumber(CONVERSIONS.euros.centsToKEuros(penalty), {
                    fractionDigits: 0,
                  })}{" "}
                  k€
                </Text>
              )}
            </div>
          ) : null}
          {description && (
            <div className={css["card-progress__description"]}>
              <Text size="sm">{description}</Text>
            </div>
          )}
        </div>
        {targetQuantity !== undefined &&
          baseQuantity !== undefined &&
          declaredQuantity !== undefined && (
            <ProgressBar
              targetQuantity={targetQuantity}
              baseQuantity={baseQuantity}
              declaredQuantity={declaredQuantity}
            />
          )}
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
    <Badge severity={severity} small>
      {targetQuantity > declaredQuantity ? t("Non atteint") : t("Atteint")}
    </Badge>
  )
}

CardProgress.DefaultBadge = DefaultBadge
