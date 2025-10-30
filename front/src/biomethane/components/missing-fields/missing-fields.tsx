import { Notice } from "common/components/notice"
import { useMissingFieldsMessages } from "./missing-fields.hooks"

export interface MissingFieldsProps {
  onPageClick?: (page: string) => void
}
export const MissingFields = ({ onPageClick }: MissingFieldsProps) => {
  const { errorMessage, digestateCount, energyCount } =
    useMissingFieldsMessages({
      onPageClick,
    })

  if (digestateCount === 0 && energyCount === 0) return null
  return (
    <Notice variant="alert" icon="fr-icon-error-line">
      <div>{errorMessage}</div>
    </Notice>
  )
}
