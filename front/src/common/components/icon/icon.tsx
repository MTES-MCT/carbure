import { fr } from "@codegouvfr/react-dsfr"
import cl from "clsx"
export interface IconProps {
  passthrough?: boolean
  size?: number
  className?: string
}
const Icon = ({ size = 24, ...props }: IconProps) => {
  return <span {...props} style={{ width: size, height: size }} />
}

export const SurveyLine = ({ className, ...props }: IconProps) => {
  return (
    <Icon {...props} className={cl(fr.cx("fr-icon-survey-line"), className)} />
  )
}
