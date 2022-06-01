import React from "react"
import { useTranslation } from "react-i18next"
import cl from "clsx"
import css from "./dialog.module.css"
import Portal from "./portal"
import Button, { ButtonVariant } from "./button"
import { Cross, Check, Return } from "./icons"
import { Overlay } from "./scaffold"

export interface DialogProps {
  className?: string
  style?: React.CSSProperties
  fullscreen?: boolean
  children: React.ReactNode
  onClose: () => void
}

export const Dialog = ({
  className,
  style,
  children,
  fullscreen,
  onClose,
}: DialogProps) => (
  <Portal onClose={onClose}>
    <div className={css.screen}>
      <Overlay onClick={onClose} />
      <div
        className={cl(css.dialog, fullscreen && css.fullscreen, className)}
        style={style}
      >
        {children}
        <Button
          variant="icon"
          icon={Cross}
          action={onClose}
          className={css.close}
        />
      </div>
    </div>
  </Portal>
)

export interface ConfirmProps {
  title: string
  description: string
  confirm: string
  variant: ButtonVariant
  icon?: React.ComponentType | React.ElementType
  onConfirm: () => Promise<any>
  onClose: () => void
}

export const Confirm = ({
  title,
  description,
  confirm,
  variant,
  icon = Check,
  onConfirm,
  onClose,
}: ConfirmProps) => {
  const { t } = useTranslation()
  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{title}</h1>
      </header>
      <main>
        <section>{description}</section>
      </main>
      <footer>
        <Button
          asideX
          icon={icon}
          variant={variant}
          label={confirm}
          action={() => onConfirm().then(onClose)}
        />
        <Button icon={Return} label={t("Retour")} action={onClose} />
      </footer>
    </Dialog>
  )
}

export default Dialog
