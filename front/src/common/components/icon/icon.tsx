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
export const SurveyFill = ({ className, ...props }: IconProps) => {
  return (
    <Icon {...props} className={cl(fr.cx("fr-icon-survey-fill"), className)} />
  )
}

export const InboxArchiveLine = ({ className, ...props }: IconProps) => {
  return (
    <Icon
      {...props}
      className={cl(fr.cx("ri-inbox-archive-line"), className)}
    />
  )
}

export const InboxArchiveFill = ({ className, ...props }: IconProps) => {
  return (
    <Icon
      {...props}
      className={cl(fr.cx("ri-inbox-archive-fill"), className)}
    />
  )
}

export const StackLine = ({ className, ...props }: IconProps) => {
  return <Icon {...props} className={cl(fr.cx("ri-stack-line"), className)} />
}

export const StackFill = ({ className, ...props }: IconProps) => {
  return <Icon {...props} className={cl(fr.cx("ri-stack-line"), className)} />
}

export const SendPlaneLine = ({ className, ...props }: IconProps) => {
  return (
    <Icon {...props} className={cl(fr.cx("ri-send-plane-line"), className)} />
  )
}

export const SendPlaneFill = ({ className, ...props }: IconProps) => {
  return (
    <Icon {...props} className={cl(fr.cx("ri-send-plane-fill"), className)} />
  )
}

export const FileTextLine = ({ className, ...props }: IconProps) => {
  return (
    <Icon {...props} className={cl(fr.cx("ri-file-text-line"), className)} />
  )
}

export const FileTextFill = ({ className, ...props }: IconProps) => {
  return (
    <Icon {...props} className={cl(fr.cx("ri-file-text-fill"), className)} />
  )
}

export const ArrowGoForwardLine = ({ className, ...props }: IconProps) => {
  return (
    <Icon
      {...props}
      className={cl(fr.cx("ri-arrow-go-forward-line"), className)}
    />
  )
}

export const ArrowGoBackLine = ({ className, ...props }: IconProps) => {
  return (
    <Icon
      {...props}
      className={cl(fr.cx("ri-arrow-go-back-line"), className)}
    />
  )
}

export const ContrastDropLine = ({ className, ...props }: IconProps) => {
  return (
    <Icon
      {...props}
      className={cl(fr.cx("ri-contrast-drop-line"), className)}
    />
  )
}

export const ContrastDropFill = ({ className, ...props }: IconProps) => {
  return (
    <Icon
      {...props}
      className={cl(fr.cx("ri-contrast-drop-fill"), className)}
    />
  )
}

export const QuestionLine = ({ className, ...props }: IconProps) => {
  return (
    <Icon {...props} className={cl(fr.cx("ri-question-line"), className)} />
  )
}

export const SettingsLine = ({ className, ...props }: IconProps) => {
  return (
    <Icon {...props} className={cl(fr.cx("ri-settings-3-line"), className)} />
  )
}

export const SettingsFill = ({ className, ...props }: IconProps) => {
  return (
    <Icon {...props} className={cl(fr.cx("ri-settings-3-line"), className)} />
  )
}
