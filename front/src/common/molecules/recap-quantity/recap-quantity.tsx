import React from "react"
import { useTranslation } from "react-i18next"
import { Text } from "common/components/text"
import css from "./recap-quantity.module.css"

interface RecapQuantityProps {
  text: string
  onRecapClick?: () => void
}

/**
 * Component used to display a summary of a quantity, and allow the user to see the details.
 */
export const RecapQuantity: React.FC<RecapQuantityProps> = ({
  text,
  onRecapClick,
}) => {
  const { t } = useTranslation()

  return (
    <div className={css["recap-quantity"]}>
      <Text size="sm">{text}</Text>
      {onRecapClick && (
        <button onClick={onRecapClick} className={css["recap-quantity-button"]}>
          <Text size="sm" is="span">
            {t("Voir le récapitulatif")}
          </Text>
        </button>
      )}
    </div>
  )
}
