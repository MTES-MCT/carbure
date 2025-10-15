import React from "react"
import { Badge } from "@codegouvfr/react-dsfr/Badge"
import { Text } from "common/components/text"
import { useTranslation } from "react-i18next"
import css from "./beta-page.module.css"

interface BetaPageProps {
  /**
   * Title to display before the "beta" badge
   */
  title?: string
  /**
   * Custom text to display after the "beta" badge
   * If not provided, uses the default translated text
   */
  text?: string
}

/**
 * Component that displays a "beta" badge followed by an information text
 * Used to indicate that a feature is in trial version
 */
export const BetaPage: React.FC<BetaPageProps> = ({ title, text }) => {
  const { t } = useTranslation()

  const defaultText = t(
    "Les actions effectuées dans cette version n'ont aucun impact réel."
  )
  const displayText = text ?? defaultText

  return (
    <div className={css["beta-page"]}>
      {title && (
        <Text is="h1" fontWeight="bold">
          {title}
        </Text>
      )}
      <Badge severity="info">BETA</Badge>
      <Text size="sm">{displayText}</Text>
    </div>
  )
}
