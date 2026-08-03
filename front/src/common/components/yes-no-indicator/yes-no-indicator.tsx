import { Icon } from "../icon"
import css from "./yes-no-indicator.module.css"

type YesNoIndicatorProps = {
  value: boolean | null | undefined
}

export const YesNoIndicator = ({ value }: YesNoIndicatorProps) =>
  value ? (
    <Icon name="fr-icon-checkbox-circle-fill" className={css.yes} />
  ) : (
    <Icon name="fr-icon-close-circle-fill" className={css.no} />
  )
