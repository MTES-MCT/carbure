import { Icon } from "../icon"

type YesNoIndicatorProps = {
  value: boolean | null | undefined
}

export const YesNoIndicator = ({ value }: YesNoIndicatorProps) =>
  value ? (
    <Icon name="fr-icon-checkbox-circle-fill" style={{ color: "green" }} />
  ) : (
    <Icon name="fr-icon-close-circle-fill" style={{ color: "red" }} />
  )
