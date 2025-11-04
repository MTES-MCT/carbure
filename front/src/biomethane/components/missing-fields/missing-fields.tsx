import { Notice } from "common/components/notice"
import { useMissingFieldsMessages } from "./hooks/use-missing-fields-message"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"

export interface MissingFieldsProps {
  onPageClick?: (page: string) => void
}
export const MissingFields = ({ onPageClick }: MissingFieldsProps) => {
  const { errorMessage, digestateCount, energyCount } =
    useMissingFieldsMessages({
      onPageClick,
    })
  const { canEditDeclaration } = useAnnualDeclaration()

  if ((digestateCount === 0 && energyCount === 0) || !canEditDeclaration)
    return null
  return (
    <Notice
      variant="alert"
      icon="fr-icon-error-line"
      data-testid="missing-fields-notice"
    >
      <div>{errorMessage}</div>
    </Notice>
  )
}
