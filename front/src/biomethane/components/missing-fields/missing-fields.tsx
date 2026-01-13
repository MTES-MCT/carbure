import { Notice } from "common/components/notice"
import { useMissingFieldsMessages } from "./hooks/use-missing-fields-message"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import css from "./missing-fields.module.css"

export interface MissingFieldsProps {
  onPageClick?: (page: string) => void
}
export const MissingFields = ({ onPageClick }: MissingFieldsProps) => {
  const { errorMessage } = useMissingFieldsMessages({
    onPageClick,
  })
  const {
    canEditDeclaration,
    currentAnnualDeclaration,
    hasAnnualDeclarationMissingObjects,
  } = useAnnualDeclaration()

  // Don't show if:
  // - User can't edit the declaration
  // - All fields are complete (no missing fields AND at least one supply input)
  // - There are missing objects (digestate or energy)
  if (
    currentAnnualDeclaration?.is_complete ||
    !canEditDeclaration ||
    hasAnnualDeclarationMissingObjects
  )
    return null

  return (
    <Notice
      variant="alert"
      icon="fr-icon-error-line"
      data-testid="missing-fields-notice"
    >
      <div className={css["missing-fields-message"]}>{errorMessage}</div>
    </Notice>
  )
}
