import React, { ReactNode } from "react"
import { useTranslation } from "react-i18next"
import cl from "clsx"
import css from "./dialog.module.css"
import Button, { ButtonVariant } from "./button"
import { Cross, Check, Return } from "./icons"
import { Overlay } from "./scaffold"
import { useMutation } from "common/hooks/async"

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
)

export interface ConfirmProps {
  title: string
  description: ReactNode
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
  const confirmAction = useMutation(onConfirm)
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
          autoFocus
          icon={icon}
          variant={variant}
          label={confirm}
          loading={confirmAction.loading}
          action={() => confirmAction.execute().then(onClose)}
        />
        <Button icon={Return} label={t("Annuler")} action={onClose} />
      </footer>
    </Dialog>
  )
}

export default Dialog
