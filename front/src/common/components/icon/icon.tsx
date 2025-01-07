import { fr, FrIconClassName, RiIconClassName } from "@codegouvfr/react-dsfr"
import cl from "clsx"
import styles from "./icon.module.css"
interface BaseIconProps {
  passthrough?: boolean
  size?: "xs" | "sm" | "md" | "lg"
  className?: string
  name: FrIconClassName | RiIconClassName
  style?: React.CSSProperties
}

export type IconName = FrIconClassName | RiIconClassName
export type IconProps = Omit<BaseIconProps, "name">

const Icon = ({ size = "md", name, ...props }: BaseIconProps) => {
  return (
    <span
      {...props}
      className={cl(props.className, styles[`fr-icon--${size}`], fr.cx(name))}
    />
  )
}

export const SurveyLine = ({ ...props }: IconProps) => {
  return <Icon {...props} name="fr-icon-survey-line" />
}

export const SurveyFill = ({ ...props }: IconProps) => {
  return <Icon {...props} name="fr-icon-survey-fill" />
}

export const InboxArchiveLine = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-inbox-archive-line" />
}

export const InboxArchiveFill = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-inbox-archive-fill" />
}

export const StackLine = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-stack-line" />
}

export const StackFill = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-stack-line" />
}

export const SendPlaneLine = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-send-plane-line" />
}

export const SendPlaneFill = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-send-plane-fill" />
}

export const FileTextLine = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-file-text-line" />
}

export const FileTextFill = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-file-text-fill" />
}

export const ArrowGoForwardLine = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-arrow-go-forward-line" />
}

export const ArrowGoBackLine = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-arrow-go-back-line" />
}

export const ContrastDropLine = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-contrast-drop-line" />
}

export const ContrastDropFill = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-contrast-drop-fill" />
}

export const QuestionLine = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-question-line" />
}

export const SettingsLine = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-settings-3-line" />
}

export const SettingsFill = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-settings-3-line" />
}

export const CalendarCheckLine = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-calendar-check-line" />
}

export const CalendarCheckFill = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-calendar-check-fill" />
}

export const BuildingLine = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-building-4-line" />
}

export const BuildingFill = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-building-4-fill" />
}

export const CheckLine = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-check-line" />
}

export const ArrowDownSLine = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-arrow-down-s-line" />
}

export const AccountLine = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-account-circle-line" />
}

export const ChartLine = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-line-chart-line" />
}

export const BookLine = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-book-2-line" />
}

export const LogoutBoxLine = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-logout-box-r-line" />
}

export const EyeLine = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-eye-line" />
}

export const EyeFill = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-eye-fill" />
}

export const ClipboardLine = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-clipboard-line" />
}

export const ClipboardFill = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-clipboard-fill" />
}

export const CircleFill = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-circle-fill" />
}

export const InformationLine = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-information-line" />
}

export const DashboardLine = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-dashboard-line" />
}

export const DashboardFill = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-dashboard-fill" />
}

export const HotelLine = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-hotel-line" />
}

export const HotelFill = ({ ...props }: IconProps) => {
  return <Icon {...props} name="ri-hotel-fill" />
}
