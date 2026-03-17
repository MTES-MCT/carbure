import { Notice } from "common/components/notice"
import { useSettingsMissingFieldsMessages } from "./hooks/use-settings-missing-fields-message"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import css from "./missing-fields.module.css"

export interface MissingFieldsSettingsProps {
  onPageClick?: (page: string) => void
}

/**
 * Bandeau d'erreurs pour les pages paramètres biométhane (contrat, site de production, site d'injection).
 * Affiche uniquement les champs manquants sur ces 3 pages.
 */
export const MissingFieldsSettings = ({
  onPageClick,
}: MissingFieldsSettingsProps) => {
  const { errorMessage } = useSettingsMissingFieldsMessages({
    onPageClick,
  })
  const { canEditDeclaration } = useAnnualDeclaration()

  if (!canEditDeclaration || errorMessage.length === 0) return null

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
