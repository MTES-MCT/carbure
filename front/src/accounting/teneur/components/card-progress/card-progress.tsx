import { ReactNode } from "react"
import { Badge } from "@codegouvfr/react-dsfr/Badge"
import { useTranslation } from "react-i18next"
import css from "./card-progress.module.css"
import { Text } from "common/components/text/text"
import { Title } from "common/components/title/title"
import { ProgressBar } from "./progress-bar"

export type CardProgressProps = {
  title?: string

  mainValue?: number
  mainText?: string
  description?: string
  children?: ReactNode

  // Objectif à atteindre
  quantityObjective: number

  quantityDeclared: number

  availableQuantity: number
}
export const CardProgress = ({
  title,
  quantityDeclared,
  quantityObjective,
  availableQuantity,
  mainText,
  mainValue,
  description,
}: CardProgressProps) => {
  const { t } = useTranslation()
  const severity = quantityObjective > quantityDeclared ? "error" : "success"
  return (
    <div className={css["card-progress"]}>
      <div className={css["card-progress__header"]}>
        {title ? (
          <Text is="span" fontWeight="bold">
            {title}
          </Text>
        ) : null}
        <Badge severity={severity}>
          {quantityObjective > quantityDeclared
            ? t("Non atteint")
            : t("Atteint")}
        </Badge>
      </div>
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
      <ProgressBar
        quantityObjective={quantityObjective}
        quantityDeclared={quantityDeclared}
        availableQuantity={availableQuantity}
      />
    </div>
  )
}
