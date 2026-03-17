import { Notice } from "common/components/notice"
import { useSettingsMissingFieldsMessages } from "./hooks/use-settings-missing-fields-message"
import css from "./missing-fields.module.css"

export interface MissingFieldsSettingsProps {
  onPageClick?: (page: string) => void
}

/**
 * Error message for settings pages (contract, production unit, injection).
 * Only shows missing fields on these 3 pages.
 */
export const MissingFieldsSettings = ({
  onPageClick,
}: MissingFieldsSettingsProps) => {
  const { errorMessage } = useSettingsMissingFieldsMessages({
    onPageClick,
  })

  if (errorMessage.length === 0) return null

  return (
    <Notice
      variant="alert"
      icon="fr-icon-error-line"
      data-testid="missing-fields-settings-notice"
    >
      <div className={css["missing-fields-message"]}>{errorMessage}</div>
    </Notice>
  )
}
