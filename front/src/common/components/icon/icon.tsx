import { fr, FrIconClassName, RiIconClassName } from "@codegouvfr/react-dsfr"
import cl from "clsx"
import styles from "./icon.module.css"
export interface IconProps {
  passthrough?: boolean
  size?: "xs" | "sm" | "md" | "lg"
  className?: string
  name: FrIconClassName | RiIconClassName
}

type IconPropsWithoutName = Omit<IconProps, "name">

const Icon = ({ size = "md", name, ...props }: IconProps) => {
  return (
    <span
      {...props}
      className={cl(props.className, styles[`fr-icon--${size}`], fr.cx(name))}
    />
  )
}

export const SurveyLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="fr-icon-survey-line" />
}

export const SurveyFill = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="fr-icon-survey-fill" />
}

export const InboxArchiveLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-inbox-archive-line" />
}

export const InboxArchiveFill = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-inbox-archive-fill" />
}

export const StackLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-stack-line" />
}

export const StackFill = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-stack-line" />
}

export const SendPlaneLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-send-plane-line" />
}

export const SendPlaneFill = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-send-plane-fill" />
}

export const FileTextLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-file-text-line" />
}

export const FileTextFill = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-file-text-fill" />
}

export const ArrowGoForwardLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-arrow-go-forward-line" />
}

export const ArrowGoBackLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-arrow-go-back-line" />
}

export const ContrastDropLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-contrast-drop-line" />
}

export const ContrastDropFill = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-contrast-drop-fill" />
}

export const QuestionLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-question-line" />
}

export const SettingsLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-settings-3-line" />
}

export const SettingsFill = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-settings-3-line" />
}

export const CalendarCheckLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-calendar-check-line" />
}

export const CalendarCheckFill = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-calendar-check-fill" />
}

export const BuildingLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-building-4-line" />
}

export const BuildingFill = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-building-4-fill" />
}

export const CheckLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-check-line" />
}

export const ArrowDownSLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-arrow-down-s-line" />
}

export const AccountLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-account-circle-line" />
}

export const ChartLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-line-chart-line" />
}

export const BookLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-book-2-line" />
}

export const BookFill = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-book-2-fill" />
}

export const LogoutBoxLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-logout-box-r-line" />
}

export const EyeLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-eye-line" />
}

export const EyeFill = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-eye-fill" />
}

export const ClipboardLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-clipboard-line" />
}

export const ClipboardFill = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-clipboard-fill" />
}

export const CircleFill = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-circle-fill" />
}

export const DashboardLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-dashboard-line" />
}

export const DashboardFill = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-dashboard-fill" />
}

export const HotelLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-hotel-line" />
}

export const HotelFill = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-hotel-fill" />
}

export const HomeLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-home-4-line" />
}

export const HomeFill = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-home-4-fill" />
}

export const FileDownloadLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-file-download-line" />
}

export const FileDownloadFill = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-file-download-fill" />
}

export const NewsPaperLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-newspaper-line" />
}

export const NewsPaperFill = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-newspaper-fill" />
}

export const TodoLine = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-todo-line" />
}

export const TodoFill = ({ ...props }: IconPropsWithoutName) => {
  return <Icon {...props} name="ri-todo-fill" />
}
